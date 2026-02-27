"""
ToolSolver — category-aware tool-calling solver for MathConstruct.

Flow per problem
----------------
1. Build an initial prompt (problem statement + formatting instructions +
   tool descriptions).
2. Send to ToolAPIQuery, which runs the multi-turn tool loop internally.
3. Collect the final assistant text (must contain \\boxed{}).
4. Optionally run parse-feedback rounds (inherited from CoTSolver).

The solver selects tools based on the problem's Tag(s) via the registry in
`math_construct.llm.tools`.
"""
from __future__ import annotations

import json
from typing import Callable

import numpy as np
from loguru import logger

from .cot_solver import CoTSolver
from ..tool_api import ToolAPIQuery
from ..tools import get_tools_for_problem
from ..tools.base_tool import BaseTool
from math_construct.problems.problem import Problem


# ---------------------------------------------------------------------------
# System prompt template
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """\
You are an expert mathematician solving competition-level math problems.

You have access to the following tools to help you compute, verify, or brute-force solutions:
{tool_list}

Strategy:
- Analyse the problem carefully.
- Choose the most appropriate tool(s) for the problem category.
- Encode the problem as a constraint / SAT / SMT / symbolic math problem when possible.
- Use multiple tools if needed to verify your answer.
- When you have found a correct answer, write it in the required format inside \\boxed{{}}.

Important:
- Always print your final answer inside \\boxed{{}} exactly as the formatting instructions require.
- Do NOT leave the answer only in tool output — re-state it in your final message.
"""

_TOOL_LIST_ITEM = "- **{name}**: {description}"


def _build_system_prompt(tools: list[BaseTool]) -> str:
    items = "\n".join(
        _TOOL_LIST_ITEM.format(name=t.name, description=t.description)
        for t in tools
    )
    return _SYSTEM_PROMPT.format(tool_list=items)


# ---------------------------------------------------------------------------
# ToolSolver
# ---------------------------------------------------------------------------

class ToolSolver(CoTSolver):
    """
    Solver that equips the LLM with math tools chosen by problem category.

    Parameters
    ----------
    base_querier_kwargs : dict
        Keyword arguments for ToolAPIQuery (model, api, temperature, etc.)
        Do NOT include `tools` — those are set per-problem.
    tool_timeout : int
        Timeout in seconds for each individual tool execution.
    max_tool_rounds : int
        Max LLM ↔ tool turns per problem before forcing a final answer.
    All other kwargs are forwarded to CoTSolver.
    """

    def __init__(
        self,
        base_querier_kwargs: dict,
        tool_timeout: int = 30,
        max_tool_rounds: int = 6,
        **cot_kwargs,
    ):
        # We pass a dummy querier to CoTSolver; the real one is built per-problem
        # to carry the correct tool set.
        self._base_querier_kwargs = base_querier_kwargs
        self._tool_timeout = tool_timeout
        self._max_tool_rounds = max_tool_rounds

        # Build a placeholder querier for the parent __init__
        # (CoTSolver only stores self.querier; we override the relevant methods)
        from ..api import APIQuery
        placeholder_querier = _PlaceholderQuerier()
        super().__init__(querier=placeholder_querier, **cot_kwargs)

    # ------------------------------------------------------------------
    # Build a ToolAPIQuery wired to the correct tools for a problem
    # ------------------------------------------------------------------

    def _make_querier_for_problem(self, problem: Problem) -> ToolAPIQuery:
        tools = get_tools_for_problem(problem, timeout=self._tool_timeout)

        def executor(tool_name: str, tool_kwargs: dict) -> str:
            tool_map = {t.name: t for t in tools}
            tool = tool_map.get(tool_name)
            if tool is None:
                return f"ToolNotFound: '{tool_name}'"
            try:
                return tool.run(**tool_kwargs)
            except Exception as e:
                return f"RuntimeError: {e}"

        return ToolAPIQuery(
            tools=tools,
            tool_executor=executor,
            max_tool_rounds=self._max_tool_rounds,
            **self._base_querier_kwargs,
        )

    # ------------------------------------------------------------------
    # Override build_query to inject tool-aware system prompt
    # ------------------------------------------------------------------

    def build_query(self, problem: Problem) -> list[dict]:
        tools = get_tools_for_problem(problem, timeout=self._tool_timeout)
        system_prompt = _build_system_prompt(tools)

        prompt = str(problem)
        prompt += f"\n\n{self.formatting_prefix}\n{problem.get_formatting()}"
        if self.give_solution:
            prompt += f"\n\nYou are given the solution: {problem.get_solution()}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
        return messages

    # ------------------------------------------------------------------
    # Override solve_initial_round to use per-problem queriers
    # ------------------------------------------------------------------

    def solve_initial_round(self, problems: list[Problem]) -> list[list[dict]]:
        logger.info("ToolSolver: performing initial round with tool calling.")
        queries = self.build_queries(problems)

        results: list[dict] = [None] * len(problems)
        costs:   list[dict] = [None] * len(problems)

        # We run problems one-by-one (or could be parallelised) because each
        # needs its own ToolAPIQuery instance with the right tools.
        for i, (problem, query) in enumerate(zip(problems, queries)):
            querier = self._make_querier_for_problem(problem)
            try:
                response_list, detailed_cost_list, total_cost = querier.run_queries([query])
                response    = response_list[0]
                detail      = detailed_cost_list[0]
            except Exception as e:
                logger.error(f"ToolAPIQuery failed for problem {i}: {e}")
                response = ""
                detail   = {"cost": 0, "input_tokens": 0, "output_tokens": 0}

            queries[i] = self.add_response(query, response)
            self.cost += detail["cost"]
            self.detailed_cost[i]["cost"]         += detail["cost"]
            self.detailed_cost[i]["input_tokens"]  += detail["input_tokens"]
            self.detailed_cost[i]["output_tokens"] += detail["output_tokens"]

        logger.info("ToolSolver: initial round done.")
        return queries

    # ------------------------------------------------------------------
    # solve() — reuse CoTSolver's parse-feedback machinery
    # ------------------------------------------------------------------

    def solve(self, problems: list[Problem]):
        self.cost = 0
        self.detailed_cost = [
            {"cost": 0, "input_tokens": 0, "output_tokens": 0}
            for _ in problems
        ]
        queries = self.solve_initial_round(problems)
        checker = [p.parse_and_check(q) for p, q in zip(problems, queries)]
        logger.info(
            f"ToolSolver: solved after initial round: "
            f"{np.mean([c[1] for c in checker]):.4f}"
        )
        queries = self.solve_parse_feedback_rounds(problems, queries)
        logger.info(f"ToolSolver: total cost = {self.cost:.4f}")
        return queries, self.detailed_cost


# ---------------------------------------------------------------------------
# Placeholder querier (never actually called — ToolSolver builds real ones)
# ---------------------------------------------------------------------------

class _PlaceholderQuerier:
    """Satisfies CoTSolver's type expectations without doing anything."""
    read_cost  = 0
    write_cost = 0

    def run_queries(self, queries):
        raise RuntimeError("_PlaceholderQuerier.run_queries should never be called.")
