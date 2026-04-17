"""
ReActToolSolver — tool-calling solver that works for any model.

Uses the ReAct (Reason + Act) prompting strategy:
  - Tools are described in plain text inside the system prompt.
  - The LLM outputs tool calls as structured text (not via API function-calling).
  - We parse the text, execute the tool, inject the result as "Observation:",
    and keep looping until the LLM writes a Final Answer containing \\boxed{}.

This means NO native tool-calling support is required from the model or API.
It works with any chat model: Llama, Mistral, GPT, Claude, etc.

Expected LLM output format (taught in system prompt):
─────────────────────────────────────────────────────
Thought: <reasoning about what to do next>
Action: <tool_name>
```python          ← or ``` for non-Python tools (MiniZinc, GAP, Lean)
<code / model to execute>
```
─────────────────────────────────────────────────────
We inject back:
─────────────────────────────────────────────────────
Observation: <tool stdout or error string>
─────────────────────────────────────────────────────
The loop ends when the LLM writes:
  Final Answer: \\boxed{<answer>}
or when max_react_iterations is reached (we then force a final-answer request).
"""
from __future__ import annotations

import copy
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

import numpy as np
from loguru import logger

from .cot_solver import CoTSolver
from ..tools import get_tools_for_problem
from ..tools.base_tool import BaseTool
from math_construct.problems.problem import Problem


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """\
You are an expert mathematician solving competition-level math problems.
You have access to specialised solver tools to help you find and verify answers.
Choose the most appropriate tool for the problem (see AVAILABLE TOOLS below).

════════════════════════════════════════════════════════════
HOW TO USE THE TOOLS  (follow this format EXACTLY)
════════════════════════════════════════════════════════════

Step 1 — Write a Thought and an Action block:

Thought: <explain what you want to compute and why, and which tool is most appropriate>
Action: <tool_name>
```python
<your complete, self-contained code here — include all imports>
```

  • <tool_name> must be one of the action labels listed in AVAILABLE TOOLS below.
  • All tools accept Python code except where noted.

Step 2 — STOP IMMEDIATELY after the closing ```.
          Do NOT write "Observation:" yourself.
          Do NOT guess what the output will be.
          The system will run your code and inject the result as:

Observation: <actual tool output>

Step 3 — Read the Observation, then either call another tool or write:

Final Answer: \\boxed{{<your answer in the exact required format>}}

════════════════════════════════════════════════════════════
AVAILABLE TOOLS
════════════════════════════════════════════════════════════
{tool_blocks}
════════════════════════════════════════════════════════════
RULES
════════════════════════════════════════════════════════════
- Use the BEST tool for the problem type (e.g. run_z3 for constraint satisfaction,
  run_ortools for combinatorics/scheduling, run_sympy for symbolic algebra,
  run_networkx for graph problems, run_python for everything else).
- NEVER write "Observation:" — only the system can do that.
- NEVER guess or simulate tool output — always run the tool.
- Your Final Answer MUST use \\boxed{{}} exactly as the formatting instructions require.
- Code must be complete and self-contained (include all imports).
- If the Observation shows an error, fix the code and try again.
"""

_FORCE_FINAL_PROMPT = (
    "You have used the maximum number of tool calls. "
    "Based on your observations so far, write your final answer now. "
    "Your answer MUST be enclosed in \\boxed{} as the formatting instructions require."
)


# ---------------------------------------------------------------------------
# ReActToolSolver
# ---------------------------------------------------------------------------

class ReActToolSolver(CoTSolver):
    """
    Tool-calling solver using text-based ReAct prompting.

    Works with any model — no native function-calling API support needed.

    Parameters
    ----------
    querier : APIQuery
        The LLM querier (standard APIQuery, not ToolAPIQuery).
    tool_timeout : int
        Seconds allowed per tool execution.
    max_react_iterations : int
        Maximum Thought→Action→Observation cycles before forcing a final answer.
    All other kwargs forwarded to CoTSolver.
    """

    def __init__(
        self,
        querier,
        tool_timeout: int = 30,
        max_react_iterations: int = 6,
        **cot_kwargs,
    ):
        super().__init__(querier=querier, **cot_kwargs)
        self.tool_timeout = tool_timeout
        self.max_react_iterations = max_react_iterations

    # ------------------------------------------------------------------
    # Build initial query with ReAct system prompt
    # ------------------------------------------------------------------

    def build_query(self, problem: Problem) -> list[dict]:
        tools = get_tools_for_problem(problem, timeout=self.tool_timeout)
        tool_blocks = "\n\n".join(t.react_prompt_block() for t in tools)
        system_content = _SYSTEM_PROMPT.format(tool_blocks=tool_blocks)

        prompt = str(problem)
        prompt += f"\n\n{self.formatting_prefix}\n{problem.get_formatting()}"
        if self.give_solution:
            prompt += f"\n\nYou are given the solution: {problem.get_solution()}"

        return [
            {"role": "system", "content": system_content},
            {"role": "user",   "content": prompt},
        ]

    # ------------------------------------------------------------------
    # ReAct loop for a single problem
    # ------------------------------------------------------------------

    def _run_react_loop(
        self,
        problem: Problem,
        messages: list[dict],
        querier,
    ) -> tuple[list[dict], dict]:
        """
        Run the Thought→Action→Observation loop for one problem.
        Returns the final message list (suitable for parse_and_check).
        """
        tools = get_tools_for_problem(problem, timeout=self.tool_timeout)
        tool_map: dict[str, BaseTool] = {t.name: t for t in tools}

        # Add stop sequence so the model cannot write "Observation:" itself.
        old_stop = querier.kwargs.get("stop")
        querier.kwargs["stop"] = ["Observation:"]
        detail = {"cost": 0, "input_tokens": 0, "output_tokens": 0}

        try:
            for iteration in range(self.max_react_iterations + 1):
                # Force final answer on last iteration
                if iteration == self.max_react_iterations:
                    messages.append({"role": "user", "content": _FORCE_FINAL_PROMPT})

                # Call the LLM
                responses, detailed_costs, cost = querier.run_queries([messages])
                response_text: str = responses[0] or ""

                # Track local cost (aggregated by caller for thread safety)
                detail["cost"] += cost["cost"]
                detail["input_tokens"] += detailed_costs[0]["input_tokens"]
                detail["output_tokens"] += detailed_costs[0]["output_tokens"]

                messages.append({"role": "assistant", "content": response_text})

                # Check if LLM gave a final answer (contains \boxed{})
                if self._has_final_answer(response_text):
                    logger.debug(f"ReAct loop finished after {iteration + 1} iteration(s).")
                    break

                # Parse tool call from the response
                tool_name, tool_input = self._parse_action(response_text)

                if tool_name is None:
                    # No action found and no final answer — nudge the model
                    logger.debug("No Action found in response. Nudging model.")
                    messages.append({
                        "role": "user",
                        "content": (
                            "Please continue. Either call a tool using the Action format, "
                            "or write your Final Answer: \\boxed{<answer>}."
                        ),
                    })
                    continue

                # Execute the tool
                tool = tool_map.get(tool_name)
                if tool is None:
                    observation = (
                        f"ToolNotFound: '{tool_name}' is not available. "
                        f"Available tools: {list(tool_map.keys())}"
                    )
                    logger.warning(observation)
                else:
                    logger.debug(f"Executing tool '{tool_name}'")
                    observation = self._execute_tool(tool, tool_name, tool_input)
                    pretty_observation = observation if observation else "<empty stdout>"
                    logger.debug(f"Observation ({tool_name}): {pretty_observation[:300]}")

                # Inject the observation as a user message
                messages.append({
                    "role": "user",
                    "content": f"Observation: {observation}",
                })
        finally:
            # Restore original stop setting
            if old_stop is None:
                querier.kwargs.pop("stop", None)
            else:
                querier.kwargs["stop"] = old_stop

        return messages, detail

    # ------------------------------------------------------------------
    # Override solve_initial_round
    # ------------------------------------------------------------------

    def solve_initial_round(self, problems: list[Problem]) -> list[list[dict]]:
        logger.info(f"ReActToolSolver: solving {len(problems)} problems.")
        queries = self.build_queries(problems)
        max_workers = max(1, int(getattr(self.querier, "concurrent_requests", 1)))
        logger.info(f"ReActToolSolver: running with {max_workers} parallel problem worker(s).")

        def _solve_one(i: int, problem: Problem, messages: list[dict]):
            local_querier = copy.deepcopy(self.querier)
            solved_messages, detail = self._run_react_loop(
                problem=problem,
                messages=messages,
                querier=local_querier,
            )
            return i, solved_messages, detail

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(_solve_one, i, problem, messages)
                for i, (problem, messages) in enumerate(zip(problems, queries))
            ]
            for future in as_completed(futures):
                i, solved_messages, detail = future.result()
                queries[i] = solved_messages
                self.cost += detail["cost"]
                self.detailed_cost[i]["cost"] += detail["cost"]
                self.detailed_cost[i]["input_tokens"] += detail["input_tokens"]
                self.detailed_cost[i]["output_tokens"] += detail["output_tokens"]

        logger.info("ReActToolSolver: initial round done.")
        return queries

    def solve(self, problems: list[Problem]):
        self.cost = 0
        self.detailed_cost = [
            {"cost": 0, "input_tokens": 0, "output_tokens": 0}
            for _ in problems
        ]
        queries = self.solve_initial_round(problems)
        checker = [p.parse_and_check(q) for p, q in zip(problems, queries)]
        logger.info(
            f"ReActToolSolver: solved after initial round: "
            f"{np.mean([c[1] for c in checker]):.4f}"
        )
        queries = self.solve_parse_feedback_rounds(problems, queries)
        logger.info(f"ReActToolSolver: total cost = {self.cost:.4f}")
        return queries, self.detailed_cost

    # ------------------------------------------------------------------
    # Parsing helpers
    # ------------------------------------------------------------------

    # Matches:   Action: <tool_name>\n```[lang]\n<code>\n```
    _ACTION_RE = re.compile(
        r"Action:\s*(?P<tool>\w+)\s*\n"   # Action: tool_name
        r"```[a-zA-Z]*\s*\n"              # opening fence (```python, ```lean, ``` etc.)
        r"(?P<code>.*?)"                  # the code block (non-greedy)
        r"```",                           # closing fence
        re.DOTALL,
    )

    def _parse_action(self, text: str) -> tuple[Optional[str], Optional[str]]:
        """
        Extract (tool_name, code_or_model) from the last Action block in `text`.
        Returns (None, None) if no Action block is found.
        """
        matches = list(self._ACTION_RE.finditer(text))
        if not matches:
            return None, None
        last = matches[-1]
        return last.group("tool").strip(), last.group("code").strip()

    def _has_final_answer(self, text: str) -> bool:
        """Return True if the text contains a \\boxed{} block (final answer)."""
        return r"\boxed{" in text

    # ------------------------------------------------------------------
    # Tool execution
    # ------------------------------------------------------------------

    def _execute_tool(self, tool: BaseTool, tool_name: str, code: str) -> str:
        """Call tool.run() with the right argument name."""
        try:
            # MiniZinc takes 'model', all others take 'code'
            if tool_name == "run_minizinc":
                return tool.run(model=code)
            elif tool_name == "run_gap":
                return tool.run(code=code)
            else:
                return tool.run(code=code)
        except Exception as e:
            return f"RuntimeError: {e}"
