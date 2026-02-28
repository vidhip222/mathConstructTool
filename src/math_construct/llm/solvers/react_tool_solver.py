"""
ReActToolSolver — tool-calling solver that works for ANY model.

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

import re
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
You have access to computational tools to help you find and verify answers.

════════════════════════════════════════════════════════════
HOW TO USE TOOLS  (follow this format EXACTLY)
════════════════════════════════════════════════════════════

To call a tool, write:

Thought: <explain your reasoning — what you want to compute and why>
Action: <tool_name>
```
<code or model for the tool>
```

After you write an Action block, you will receive:

Observation: <output returned by the tool>

You may call as many tools as you need.
When you have a verified final answer, write:

Final Answer: \\boxed{<your answer in the required format>}

════════════════════════════════════════════════════════════
AVAILABLE TOOLS
════════════════════════════════════════════════════════════
{tool_blocks}
════════════════════════════════════════════════════════════
STRATEGY
════════════════════════════════════════════════════════════
1. Read the problem carefully. Identify the mathematical category.
2. Choose the most suitable tool (see "Best for" in each tool description).
3. Encode the problem constraints precisely — wrong encoding = wrong answer.
4. Run the tool and read the Observation.
5. If the Observation is an error, fix the code and try again.
6. Verify your answer with a second tool call if possible.
7. Write the Final Answer in the exact format specified in the problem.

IMPORTANT:
- Your Final Answer MUST be inside \\boxed{{}} exactly as the formatting instructions require.
- Do NOT put the answer only in tool output — state it explicitly in your Final Answer line.
- Tool code must be complete and self-contained (all imports included).
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

    def _run_react_loop(self, problem: Problem, messages: list[dict]) -> list[dict]:
        """
        Run the Thought→Action→Observation loop for one problem.
        Returns the final message list (suitable for parse_and_check).
        """
        tools = get_tools_for_problem(problem, timeout=self.tool_timeout)
        tool_map: dict[str, BaseTool] = {t.name: t for t in tools}

        for iteration in range(self.max_react_iterations + 1):
            # Force final answer on last iteration
            if iteration == self.max_react_iterations:
                messages.append({"role": "user", "content": _FORCE_FINAL_PROMPT})

            # Call the LLM
            responses, detailed_costs, cost = self.querier.run_queries([messages])
            response_text: str = responses[0] or ""

            self.cost += cost["cost"]
            # We track cost in the caller (solve_initial_round), so no detailed_cost here

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
                logger.debug(f"Observation ({tool_name}): {observation[:300]}")

            # Inject the observation as a user message
            messages.append({
                "role": "user",
                "content": f"Observation: {observation}",
            })

        return messages

    # ------------------------------------------------------------------
    # Override solve_initial_round
    # ------------------------------------------------------------------

    def solve_initial_round(self, problems: list[Problem]) -> list[list[dict]]:
        logger.info(f"ReActToolSolver: solving {len(problems)} problems.")
        queries = self.build_queries(problems)

        for i, (problem, messages) in enumerate(zip(problems, queries)):
            queries[i] = self._run_react_loop(problem, messages)

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
