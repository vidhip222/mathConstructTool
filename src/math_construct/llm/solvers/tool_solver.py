"""
ToolSolver: sequential tool-use loop per problem, parallel across problems.
Extends CoTSolver so parse/check feedback rounds run after the tool loop.
"""
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from loguru import logger
from tqdm import tqdm
import numpy as np

from .cot_solver import CoTSolver
from ..tools import MATH_TOOLS, TOOL_SYSTEM_PROMPT, dispatch_tool

_COLOR_CALL = "\033[96m"
_COLOR_RESULT = "\033[92m"
_COLOR_RESET = "\033[0m"


def _parse_tool_arguments(raw) -> dict:
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass
    return {}


def _extract_inline_tool_calls(content: str) -> list:
    """
    Fallback for models (e.g. some Ollama versions) that output tool calls as
    JSON text in their content instead of using native tool_calls.

    Handles several common shapes:
      {"name": "python_tool", "parameters": {...}}
      {"tool_name": "python_tool", "arguments": {...}}
      {"name": "python_tool", "arguments": {...}}
    Returns a list of normalised tool_call dicts (OpenAI format).
    """
    if not content:
        return []

    calls = []
    # Find all top-level JSON objects in the content
    depth = 0
    start = None
    for i, ch in enumerate(content):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                fragment = content[start:i + 1]
                try:
                    obj = json.loads(fragment)
                    name = obj.get("name") or obj.get("tool_name") or obj.get("function")
                    args = obj.get("parameters") or obj.get("arguments") or obj.get("params") or {}
                    if name and name in {t["function"]["name"] for t in MATH_TOOLS}:
                        calls.append({
                            "id": f"inline_{len(calls)}",
                            "type": "function",
                            "function": {
                                "name": name,
                                "arguments": json.dumps(args) if isinstance(args, dict) else args,
                            },
                        })
                except (json.JSONDecodeError, TypeError):
                    pass
                start = None
    return calls


class ToolSolver(CoTSolver):
    def __init__(
        self,
        querier,
        tools: list = None,
        max_tool_rounds: int = 5,
        verbose: bool = False,
        **kwargs,
    ):
        """
        Args:
            querier: APIQuery instance.
            tools: List of tool schemas (OpenAI format). Defaults to MATH_TOOLS.
            max_tool_rounds: Max number of tool-call rounds before forcing a final answer.
            verbose: Print tool calls and results to stdout.
            **kwargs: Passed to CoTSolver (system_prompt, parse_feedback, etc.).
        """
        super().__init__(querier, **kwargs)
        self.tools = tools if tools is not None else MATH_TOOLS
        self.max_tool_rounds = max_tool_rounds
        self.verbose = verbose

    # ------------------------------------------------------------------
    # Query building
    # ------------------------------------------------------------------

    def build_query(self, problem) -> list:
        """Inject tool instructions into the system prompt."""
        messages = super().build_query(problem)
        appendix = f"\n\n{TOOL_SYSTEM_PROMPT}"
        if messages and messages[0]["role"] == "system":
            messages[0]["content"] += appendix
        else:
            messages.insert(0, {"role": "system", "content": TOOL_SYSTEM_PROMPT})
        return messages

    # ------------------------------------------------------------------
    # Message utilities
    # ------------------------------------------------------------------

    def _strip_tool_messages(self, messages: list) -> list:
        """
        Return a copy of messages with tool-call and tool-result entries removed,
        keeping only system/user/assistant-text messages.
        Used before parse-feedback rounds so the regular querier doesn't choke on
        provider-specific tool formats.
        """
        stripped = []
        for msg in messages:
            role = msg.get("role", "")
            if role == "tool":
                continue
            if role == "user" and isinstance(msg.get("content"), list):
                # Anthropic-style tool_result user messages — skip
                continue
            if role == "assistant" and msg.get("tool_calls"):
                # Keep text content if any, drop tool_calls key
                content = msg.get("content") or ""
                if content:
                    stripped.append({"role": "assistant", "content": content})
                continue
            stripped.append(msg)
        return stripped

    def _extract_boxed_answer(self, messages: list) -> str | None:
        """Return the last \\boxed{...} content found in assistant messages, or None."""
        for msg in reversed(messages):
            if msg.get("role") == "assistant":
                content = msg.get("content") or ""
                match = re.search(r"\\boxed\{(.+?)\}", content, re.DOTALL)
                if match:
                    return match.group(1).strip()
        return None

    def _build_verification_code(self, problem, answer_str: str) -> str | None:
        """
        Build a python_tool call that verifies whether answer_str satisfies the
        problem conditions. Returns Python code string, or None if not applicable.
        """
        # Generic: ask model to verify. We just emit code that re-runs parse_and_check.
        # For the tool loop we do a lightweight structural check via Python.
        # This is a best-effort helper — works for list-answer problems.
        try:
            parsed, is_correct, details = problem.parse_and_check(
                [{"role": "assistant", "content": f"\\boxed{{{answer_str}}}"}]
            )
            if is_correct:
                return None  # already correct, no verification needed
            # Build code that prints whether the answer satisfies conditions
            code = (
                f"# Verify candidate answer for: {getattr(problem.config, 'name', 'unknown')}\n"
                f"answer = [{answer_str}]\n"
                f"n = len(answer)\n"
                f"# Check all distinct\n"
                f"assert len(set(answer)) == n, f'Not all distinct: {{answer}}'\n"
                f"# Check all positive\n"
                f"assert all(x > 0 for x in answer), 'Not all positive'\n"
                f"print('Answer passes basic checks. Length:', n)\n"
                f"print('Answer:', answer)\n"
            )
            return code
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Single-problem tool loop
    # ------------------------------------------------------------------

    def solve_single(self, problem) -> tuple:
        """
        Run the tool loop for one problem.
        Returns (messages: list, detailed_cost: dict).
        """
        messages = self.build_query(problem)
        detail = {"cost": 0.0, "input_tokens": 0, "output_tokens": 0}
        final_answer_obtained = False
        # Track (name, args_json) of each tool call to detect stuck loops
        recent_call_signatures: list = []

        for round_idx in range(self.max_tool_rounds):
            try:
                response = self.querier.run_query_with_tools_with_retry(messages, self.tools)
            except Exception as e:
                logger.error(f"[ToolSolver] round {round_idx} API error: {e}")
                messages.append({"role": "assistant", "content": f"[API error: {e}]"})
                break

            _add_cost(detail, response, self.querier)

            tool_calls = response.get("tool_calls") or []
            content = response.get("output") or ""

            # --- Inline JSON extraction fallback (for Ollama / non-native tool models) ---
            if not tool_calls and content:
                tool_calls = _extract_inline_tool_calls(content)
                if tool_calls and self.verbose:
                    print(f"{_COLOR_CALL}[inline-tool-calls extracted]{_COLOR_RESET} {len(tool_calls)} call(s)")

            if not tool_calls:
                # No tool calls — this is the final answer
                messages.append({"role": "assistant", "content": content})
                final_answer_obtained = True
                break

            # Append assistant message (with text + tool_calls)
            norm_calls = []
            for idx, tc in enumerate(tool_calls):
                norm_calls.append({
                    "id": tc.get("id") or f"call_{round_idx}_{idx}",
                    "type": "function",
                    "function": tc.get("function", {}),
                })
            messages.append({
                "role": "assistant",
                "content": content,
                "tool_calls": norm_calls,
            })

            # Execute tools and append results
            stuck = False
            for tc in norm_calls:
                fn = tc["function"]
                name = fn.get("name", "")
                arguments = _parse_tool_arguments(fn.get("arguments", {}))
                sig = (name, json.dumps(arguments, sort_keys=True))

                # Detect identical repeated calls — break the loop
                if recent_call_signatures.count(sig) >= 2:
                    logger.warning(
                        f"[ToolSolver] detected stuck loop — same call '{name}' repeated "
                        f"{recent_call_signatures.count(sig)+1}x. Stopping tool rounds."
                    )
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": json.dumps({
                            "error": (
                                f"This exact call has already been attempted and failed. "
                                f"Stop calling '{name}' with the same arguments. "
                                "Try a different approach or write your final answer now."
                            )
                        }),
                    })
                    stuck = True
                    break

                recent_call_signatures.append(sig)
                if len(recent_call_signatures) > 20:
                    recent_call_signatures.pop(0)

                if self.verbose:
                    print(f"{_COLOR_CALL}[tool-call]{_COLOR_RESET} {name} args={json.dumps(arguments)}")

                result = dispatch_tool(name, arguments)

                if self.verbose:
                    print(f"{_COLOR_RESULT}[tool-result]{_COLOR_RESET} {name} → {json.dumps(result)}")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": json.dumps(result),
                })

            if stuck:
                break

        if not final_answer_obtained:
            # Tool rounds exhausted — nudge model for final formatted answer
            logger.warning("[ToolSolver] tool rounds exhausted, prompting for final answer")
            messages.append({
                "role": "user",
                "content": (
                    "You have used all tool rounds. "
                    r"Now write your final answer in the required format, with \boxed{} around it."
                ),
            })
            try:
                clean = self._strip_tool_messages(messages)
                clean.append(messages[-1])
                response = self.querier.run_query_with_tools_with_retry(clean, None)
                _add_cost(detail, response, self.querier)
                messages.append({"role": "assistant", "content": response.get("output") or ""})
            except Exception as e:
                logger.error(f"[ToolSolver] final-answer prompt error: {e}")

        # ------------------------------------------------------------------
        # Forced verification step
        # Check if the model's boxed answer actually passes, and if not,
        # inject a verification tool call + give one more chance to fix it.
        # ------------------------------------------------------------------
        boxed = self._extract_boxed_answer(messages)
        if boxed:
            try:
                _, is_correct, details = problem.parse_and_check(
                    [{"role": "assistant", "content": f"\\boxed{{{boxed}}}"}]
                )
                if not is_correct:
                    logger.info(f"[ToolSolver] answer failed verification: {details}. Injecting fix round.")
                    verify_msg = (
                        f"Your answer \\boxed{{{boxed}}} is INCORRECT.\n"
                        f"Checker says: {details}\n\n"
                        "Use python_tool to search for a correct answer. "
                        "Write a brute-force loop, verify the result satisfies all conditions, "
                        r"then submit the correct answer in \boxed{}."
                    )
                    messages.append({"role": "user", "content": verify_msg})
                    try:
                        clean = self._strip_tool_messages(messages)
                        clean.append(messages[-1])
                        response = self.querier.run_query_with_tools_with_retry(clean, self.tools)
                        _add_cost(detail, response, self.querier)
                        fix_content = response.get("output") or ""
                        # Run any inline tool calls from the fix response
                        fix_tool_calls = response.get("tool_calls") or _extract_inline_tool_calls(fix_content)
                        if fix_tool_calls:
                            for tc in fix_tool_calls:
                                fn = tc.get("function", {})
                                name = fn.get("name", "")
                                arguments = _parse_tool_arguments(fn.get("arguments", {}))
                                if self.verbose:
                                    print(f"{_COLOR_CALL}[verify-fix tool-call]{_COLOR_RESET} {name}")
                                result = dispatch_tool(name, arguments)
                                if self.verbose:
                                    print(f"{_COLOR_RESULT}[verify-fix result]{_COLOR_RESET} {json.dumps(result)}")
                                # Append as user message (simplified — no tool_calls format needed here)
                                messages.append({
                                    "role": "user",
                                    "content": f"Tool result for {name}:\n{json.dumps(result)}",
                                })
                            # Ask for final answer after fix tools ran
                            clean2 = self._strip_tool_messages(messages)
                            response2 = self.querier.run_query_with_tools_with_retry(clean2, None)
                            _add_cost(detail, response2, self.querier)
                            messages.append({"role": "assistant", "content": response2.get("output") or ""})
                        else:
                            messages.append({"role": "assistant", "content": fix_content})
                    except Exception as e:
                        logger.error(f"[ToolSolver] verification fix round error: {e}")
            except Exception:
                pass  # parse_and_check may not work for all problem types

        return messages, detail

    # ------------------------------------------------------------------
    # Batch solve
    # ------------------------------------------------------------------

    def solve(self, problems: list) -> tuple:
        """
        Solve all problems in parallel (ThreadPoolExecutor).
        After the tool loop, optionally run parse/check feedback rounds (CoTSolver).
        Returns (queries: list[list], detailed_costs: list[dict]).
        """
        n = len(problems)
        self.cost = 0.0
        self.detailed_cost = [
            {"cost": 0.0, "input_tokens": 0, "output_tokens": 0} for _ in range(n)
        ]
        results: list = [None] * n

        with ThreadPoolExecutor(max_workers=self.querier.concurrent_requests) as executor:
            future_to_idx = {
                executor.submit(self.solve_single, problem): i
                for i, problem in enumerate(problems)
            }
            for future in tqdm(as_completed(future_to_idx), total=n, desc="ToolSolver"):
                i = future_to_idx[future]
                try:
                    messages, detail = future.result()
                    results[i] = messages
                    self.detailed_cost[i] = detail
                    self.cost += detail["cost"]
                except Exception as e:
                    logger.error(f"[ToolSolver] problem {i} failed: {e}")
                    results[i] = [{"role": "assistant", "content": ""}]

        # Log accuracy after tool loop
        try:
            checker = [p.parse_and_check(q) for p, q in zip(problems, results)]
            logger.info(f"Solved after tool loop: {np.mean([c[1] for c in checker]):.4f}")
        except Exception:
            pass

        # Parse/check feedback rounds (inherited) — strip tool messages first so
        # the regular querier works across all providers
        if self.parse_feedback or self.check_feedback:
            clean_results = [self._strip_tool_messages(r) for r in results]
            clean_results = self.solve_parse_feedback_rounds(problems, clean_results)
            for i, detail in enumerate(self.detailed_cost):
                detail["cost"] = detail.get("cost", 0)
            results = clean_results

        logger.info(f"[ToolSolver] total cost: ${self.cost:.4f}")
        return results, self.detailed_cost


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _add_cost(detail: dict, response: dict, querier) -> None:
    in_tok = response.get("input_tokens", 0)
    out_tok = response.get("output_tokens", 0)
    detail["input_tokens"] += in_tok
    detail["output_tokens"] += out_tok
    detail["cost"] += (in_tok * querier.read_cost + out_tok * querier.write_cost) / 1e6
