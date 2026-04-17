import time

from math_construct.llm.solvers.tool_solver import ToolSolver
from math_construct.llm.tool_api import ToolAPIQuery
from scripts.run import _model_requires_react_for_tool_calls


class _DummyProblem:
    class config:
        tags = []
        parameters = []

    def __init__(self, idx: int):
        self.idx = idx

    def __str__(self):
        return f"Problem {self.idx}"

    def get_formatting(self):
        return r"Put final answer in \\boxed{}"

    def get_solution(self):
        return self.idx

    def parse_and_check(self, _messages):
        return None, False, "not used"


class _FakeQuerier:
    def __init__(self, idx: int):
        self.idx = idx

    def run_queries(self, _queries):
        # Force out-of-order completion if executed in parallel.
        time.sleep(0.04 if self.idx == 0 else 0.0)
        return [f"answer_{self.idx}"], [{"cost": 0.0, "input_tokens": 1, "output_tokens": 1}], {"cost": 0.0}


class _ParallelTestToolSolver(ToolSolver):
    def _make_querier_for_problem(self, problem):
        return _FakeQuerier(problem.idx)


def test_tool_solver_parallel_initial_round_preserves_problem_order():
    solver = _ParallelTestToolSolver(
        base_querier_kwargs={"concurrent_requests": 4},
        parse_feedback=False,
        check_feedback=False,
    )
    problems = [_DummyProblem(0), _DummyProblem(1), _DummyProblem(2)]
    solver.cost = 0
    solver.detailed_cost = [{"cost": 0, "input_tokens": 0, "output_tokens": 0} for _ in problems]

    queries = solver.solve_initial_round(problems)

    # Query i should contain the response generated from problem i.
    for i, q in enumerate(queries):
        assert q[-1]["role"] == "assistant"
        assert q[-1]["content"] == f"answer_{i}"


def test_large_openai_models_are_routed_to_react_mode():
    assert _model_requires_react_for_tool_calls("openai", "gpt-5")
    assert _model_requires_react_for_tool_calls("openai", "o3-mini")
    assert not _model_requires_react_for_tool_calls("openai", "gpt-4o")
    assert not _model_requires_react_for_tool_calls("together", "gpt-5")


def test_tool_api_query_respects_system_role_conversion(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    query = ToolAPIQuery(
        model="gpt-5",
        api="openai",
        tools=[],
        tool_executor=lambda _name, _kwargs: "ok",
    )

    messages = query._prepare_query_messages([
        {"role": "system", "content": "system prompt"},
        {"role": "user", "content": "hello"},
    ])

    assert messages[0]["role"] == "developer"
    assert messages[0]["content"] == "system prompt"
