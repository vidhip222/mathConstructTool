"""
Tests for ToolSolver and math tools.
Mirrors the structure of math-constraint-main/tests/test_eval.py.
Run with:  pytest tests/test_tool_solver.py -v
"""
import json
import pytest

from math_construct.llm.tools import (
    _safe_calculate,
    _sympy_compute,
    _execute_python,
    _z3_solve,
    _solve_cnf,
    _or_solve,
    dispatch_tool,
    MATH_TOOLS,
    TOOL_SYSTEM_PROMPT,
)
from math_construct.llm.solvers.tool_solver import ToolSolver, _parse_tool_arguments


# ---------------------------------------------------------------------------
# Stub APIQuery — returns scripted responses
# ---------------------------------------------------------------------------

class _StubAPIQuery:
    """Minimal APIQuery stand-in for unit testing ToolSolver."""

    def __init__(self, responses: list):
        """
        responses: list of dicts, each representing one call to run_query_with_tools.
        Each dict may have:
            "output"     : str   (assistant text, default "")
            "tool_calls" : list  (OpenAI-format tool calls, default [])
            "input_tokens" / "output_tokens" : int (default 1)
        """
        self.responses = list(responses)
        self.calls: list = []
        self.read_cost = 1.0
        self.write_cost = 1.0
        self.concurrent_requests = 4
        self.max_retries = 1
        self.sleep_on_error = 0
        self.sleep_after_request = 0
        self.throw_error_on_failure = False

    def run_query_with_tools_with_retry(self, messages, tools):
        self.calls.append({"messages": messages, "tools": tools})
        if not self.responses:
            raise RuntimeError("No stub responses left")
        return self._normalise(self.responses.pop(0))

    def run_query_with_retry(self, query):
        self.calls.append({"messages": query, "tools": None})
        if not self.responses:
            raise RuntimeError("No stub responses left")
        return self._normalise(self.responses.pop(0))

    def run_queries(self, queries):
        results = []
        for q in queries:
            results.append(self.run_query_with_retry(q))
        detailed = [
            {"cost": 0.0, "input_tokens": r.get("input_tokens", 1),
             "output_tokens": r.get("output_tokens", 1)}
            for r in results
        ]
        cost = {"cost": 0.0, "input_tokens": 0, "output_tokens": 0}
        return [r["output"] for r in results], detailed, cost

    @staticmethod
    def _normalise(r: dict) -> dict:
        return {
            "output": r.get("output", ""),
            "tool_calls": r.get("tool_calls", []),
            "input_tokens": r.get("input_tokens", 1),
            "output_tokens": r.get("output_tokens", 1),
        }


# ---------------------------------------------------------------------------
# Minimal Problem stub for ToolSolver.solve() tests
# ---------------------------------------------------------------------------

class _StubProblem:
    """Minimal Problem-like object for ToolSolver tests."""

    class config:
        parameters = []
        timeout = 5

    def __str__(self):
        return "Find x such that x^2 = 4."

    def get_formatting(self):
        return r"Wrap the answer in \boxed{}."

    def get_solution(self):
        return [2]

    def parse_and_check(self, messages):
        # Accept any message containing \boxed{2}
        for msg in reversed(messages):
            if isinstance(msg, dict) and r"\boxed{2}" in msg.get("content", ""):
                return 2, True, "Correct"
        return None, False, r"No \boxed{2} found"

    def parse(self, output_str):
        # Match real Problem.parse: raise when not found (so feedback kicks in)
        if isinstance(output_str, list):
            text = " ".join(m.get("content", "") for m in output_str if isinstance(m, dict))
        else:
            text = str(output_str)
        if r"\boxed{2}" in text:
            return 2
        raise Exception(r"No \boxed content found. Final solution needs to be encased in \boxed{}.")


# ---------------------------------------------------------------------------
# Tests: individual tool functions
# ---------------------------------------------------------------------------

class TestCalculator:
    def test_addition(self):
        r = _safe_calculate("3 + 4")
        assert r["ok"] is True
        assert r["result"] == 7

    def test_power(self):
        r = _safe_calculate("2**10")
        assert r["ok"] is True
        assert r["result"] == 1024

    def test_floor_division(self):
        r = _safe_calculate("17 // 5")
        assert r["ok"] is True
        assert r["result"] == 3

    def test_complex_expression(self):
        r = _safe_calculate("(100 - 1) * (100 + 1)")
        assert r["ok"] is True
        assert r["result"] == 9999

    def test_invalid_expression(self):
        r = _safe_calculate("__import__('os').system('ls')")
        assert r["ok"] is False

    def test_empty_expression(self):
        r = _safe_calculate("")
        assert r["ok"] is False


class TestSympyTool:
    def test_gcd(self):
        r = _sympy_compute("gcd", ["12", "18"])
        assert r["ok"] is True
        assert r["result"] == 6

    def test_lcm(self):
        r = _sympy_compute("lcm", ["4", "6"])
        assert r["ok"] is True
        assert r["result"] == 12

    def test_isprime_true(self):
        r = _sympy_compute("isprime", ["17"])
        assert r["ok"] is True
        assert r["result"] is True

    def test_isprime_false(self):
        r = _sympy_compute("isprime", ["15"])
        assert r["ok"] is True
        assert r["result"] is False

    def test_factorint(self):
        r = _sympy_compute("factorint", ["12"])
        assert r["ok"] is True
        assert r["result"] == {"2": 2, "3": 1}

    def test_totient(self):
        r = _sympy_compute("totient", ["10"])
        assert r["ok"] is True
        assert r["result"] == 4

    def test_binomial(self):
        r = _sympy_compute("binomial", ["10", "3"])
        assert r["ok"] is True
        assert r["result"] == 120

    def test_factor_polynomial(self):
        r = _sympy_compute("factor", ["x**2 - 1"])
        assert r["ok"] is True
        assert "(x - 1)" in r["result"] and "(x + 1)" in r["result"]

    def test_solve_quadratic(self):
        r = _sympy_compute("solve", ["x**2 - 4", "x"])
        assert r["ok"] is True
        assert set(r["result"]) == {"-2", "2"}

    def test_floor(self):
        r = _sympy_compute("floor", ["3.7"])
        assert r["ok"] is True
        assert r["result"] == 3

    def test_unknown_operation(self):
        r = _sympy_compute("frobulate", ["1"])
        assert r["ok"] is False
        assert "Unknown operation" in r["error"]


class TestPythonTool:
    def test_simple_print(self):
        r = _execute_python("print(2 + 2)")
        assert r["ok"] is True
        assert "4" in r["stdout"]

    def test_sympy_available(self):
        r = _execute_python("from sympy import factorint; print(factorint(12))")
        assert r["ok"] is True
        assert "2" in r["stdout"]

    def test_timeout(self):
        r = _execute_python("import time; time.sleep(5)", timeout=1)
        assert r["timed_out"] is True

    def test_runtime_error(self):
        r = _execute_python("raise ValueError('boom')")
        assert r["ok"] is False

    def test_itertools_available(self):
        r = _execute_python(
            "import itertools; print(list(itertools.permutations([1,2,3])))"
        )
        assert r["ok"] is True
        assert "1" in r["stdout"]


class TestZ3Tool:
    def test_simple_sat(self):
        code = "s=Solver(); x=Int('x'); s.add(x>0, x<5); print('SAT' if s.check()==sat else 'UNSAT')"
        r = _z3_solve(code)
        assert r["ok"] is True
        assert "SAT" in r["stdout"]

    def test_unsat(self):
        code = "s=Solver(); x=Int('x'); s.add(x>5, x<3); print('SAT' if s.check()==sat else 'UNSAT')"
        r = _z3_solve(code)
        assert r["ok"] is True
        assert "UNSAT" in r["stdout"]


class TestSolveCnf:
    def test_trivially_sat(self):
        r = _solve_cnf([[1]])
        assert r["ok"] is True
        assert r["satisfiable"] is True
        assert 1 in (r["model"] or [])

    def test_unsat(self):
        r = _solve_cnf([[1], [-1]])
        assert r["ok"] is True
        assert r["satisfiable"] is False

    def test_dimacs_sat(self):
        dimacs = "p cnf 2 2\n1 2 0\n-1 0\n"
        r = _solve_cnf(dimacs, max_var=2)
        assert r["ok"] is True
        assert r["satisfiable"] is True
        assert -1 in (r["model"] or [])
        assert 2 in (r["model"] or [])

    def test_dimacs_unsat(self):
        dimacs = "p cnf 1 2\n1 0\n-1 0\n"
        r = _solve_cnf(dimacs, max_var=1)
        assert r["ok"] is True
        assert r["satisfiable"] is False

    def test_empty_clauses(self):
        r = _solve_cnf([])
        assert r["ok"] is True
        assert r["satisfiable"] is True

    def test_invalid_input(self):
        r = _solve_cnf(42)
        assert r["ok"] is False


class TestDispatchTool:
    def test_calculator(self):
        r = dispatch_tool("calculator", {"expression": "6 * 7"})
        assert r["ok"] is True
        assert r["result"] == 42

    def test_sympy(self):
        r = dispatch_tool("sympy_tool", {"operation": "gcd", "args": ["8", "12"]})
        assert r["ok"] is True
        assert r["result"] == 4

    def test_python(self):
        r = dispatch_tool("python_tool", {"code": "print(42)"})
        assert r["ok"] is True
        assert "42" in r["stdout"]

    def test_solve_cnf(self):
        r = dispatch_tool("solve_cnf", {"cnf": [[1, 2], [-1]], "max_var": 2})
        assert r["ok"] is True
        assert r["satisfiable"] is True

    def test_unknown_tool(self):
        r = dispatch_tool("blorp", {})
        assert r["ok"] is False
        assert "Unknown tool" in r["error"]


# ---------------------------------------------------------------------------
# Tests: _parse_tool_arguments
# ---------------------------------------------------------------------------

class TestParseToolArguments:
    def test_dict_passthrough(self):
        d = {"a": 1}
        assert _parse_tool_arguments(d) == d

    def test_json_string(self):
        s = '{"expression": "1+2"}'
        assert _parse_tool_arguments(s) == {"expression": "1+2"}

    def test_invalid_string(self):
        assert _parse_tool_arguments("not json") == {}

    def test_none(self):
        assert _parse_tool_arguments(None) == {}


# ---------------------------------------------------------------------------
# Tests: ToolSolver — tool loop
# ---------------------------------------------------------------------------

class TestToolSolverLoop:
    def _make_problem(self):
        return _StubProblem()

    def test_no_tool_calls_immediate_answer(self):
        """Model answers directly without using any tools."""
        querier = _StubAPIQuery([
            {"output": r"The answer is \boxed{2}.", "tool_calls": []},
        ])
        solver = ToolSolver(querier=querier, max_tool_rounds=5)
        problem = self._make_problem()
        messages, detail = solver.solve_single(problem)

        assert any(r"\boxed{2}" in m.get("content", "") for m in messages)
        assert len(querier.calls) == 1
        assert detail["input_tokens"] == 1

    def test_one_tool_call_then_answer(self):
        """Model calls calculator once, then answers."""
        querier = _StubAPIQuery([
            {
                "output": "Let me compute.",
                "tool_calls": [{
                    "id": "c1",
                    "type": "function",
                    "function": {"name": "calculator", "arguments": '{"expression": "2**2"}'},
                }],
            },
            {"output": r"So the answer is \boxed{2}.", "tool_calls": []},
        ])
        solver = ToolSolver(querier=querier, max_tool_rounds=5)
        messages, detail = solver.solve_single(self._make_problem())

        # Check conversation structure
        roles = [m["role"] for m in messages]
        assert "tool" in roles
        assert roles.count("assistant") >= 2

        # Check tool result was appended
        tool_msgs = [m for m in messages if m["role"] == "tool"]
        assert len(tool_msgs) == 1
        tool_result = json.loads(tool_msgs[0]["content"])
        assert tool_result["ok"] is True
        assert tool_result["result"] == 4

        assert any(r"\boxed{2}" in m.get("content", "") for m in messages)
        assert len(querier.calls) == 2

    def test_multiple_tool_calls(self):
        """Three tools in sequence, then final answer."""
        querier = _StubAPIQuery([
            {
                "output": "",
                "tool_calls": [{
                    "id": "c1", "type": "function",
                    "function": {"name": "calculator", "arguments": '{"expression": "1+1"}'},
                }],
            },
            {
                "output": "",
                "tool_calls": [{
                    "id": "c2", "type": "function",
                    "function": {"name": "sympy_tool", "arguments": '{"operation": "isprime", "args": ["2"]}'},
                }],
            },
            {
                "output": "",
                "tool_calls": [{
                    "id": "c3", "type": "function",
                    "function": {"name": "python_tool", "arguments": '{"code": "print(2)"}'},
                }],
            },
            {"output": r"Final answer: \boxed{2}.", "tool_calls": []},
        ])
        solver = ToolSolver(querier=querier, max_tool_rounds=5)
        messages, _ = solver.solve_single(self._make_problem())

        tool_msgs = [m for m in messages if m["role"] == "tool"]
        assert len(tool_msgs) == 3
        assert len(querier.calls) == 4
        assert any(r"\boxed{2}" in m.get("content", "") for m in messages)

    def test_max_rounds_exhaustion_prompts_final_answer(self):
        """When max_tool_rounds is 2, the solver nudges for a final answer."""
        tool_response = {
            "output": "",
            "tool_calls": [{
                "id": "cx", "type": "function",
                "function": {"name": "calculator", "arguments": '{"expression": "1"}'},
            }],
        }
        querier = _StubAPIQuery([
            tool_response.copy(),
            tool_response.copy(),
            # nudge response
            {"output": r"After tools: \boxed{2}.", "tool_calls": []},
        ])
        solver = ToolSolver(querier=querier, max_tool_rounds=2)
        messages, _ = solver.solve_single(self._make_problem())

        assert any(r"\boxed{2}" in m.get("content", "") for m in messages)

    def test_unknown_tool_returns_error_in_message(self):
        """Calling a non-existent tool should append an error result and continue."""
        querier = _StubAPIQuery([
            {
                "output": "",
                "tool_calls": [{
                    "id": "c1", "type": "function",
                    "function": {"name": "nonexistent_tool", "arguments": "{}"},
                }],
            },
            {"output": r"Answer: \boxed{2}.", "tool_calls": []},
        ])
        solver = ToolSolver(querier=querier, max_tool_rounds=5)
        messages, _ = solver.solve_single(self._make_problem())

        tool_msgs = [m for m in messages if m["role"] == "tool"]
        assert len(tool_msgs) == 1
        result = json.loads(tool_msgs[0]["content"])
        assert result["ok"] is False
        assert "Unknown tool" in result["error"]

    def test_tool_system_prompt_injected(self):
        """Tool instructions must appear in the system message."""
        querier = _StubAPIQuery([
            {"output": r"\boxed{2}", "tool_calls": []},
        ])
        solver = ToolSolver(querier=querier, max_tool_rounds=5)
        messages, _ = solver.solve_single(self._make_problem())

        system_msgs = [m for m in messages if m["role"] == "system"]
        assert system_msgs, "System message missing"
        assert "calculator" in system_msgs[0]["content"]
        assert "sympy_tool" in system_msgs[0]["content"]

    def test_tools_passed_to_api(self):
        """The API must receive the tool schemas on every tool-use round."""
        querier = _StubAPIQuery([
            {
                "output": "",
                "tool_calls": [{
                    "id": "c1", "type": "function",
                    "function": {"name": "calculator", "arguments": '{"expression": "1"}'},
                }],
            },
            {"output": r"\boxed{2}", "tool_calls": []},
        ])
        solver = ToolSolver(querier=querier, max_tool_rounds=5)
        solver.solve_single(self._make_problem())

        # First call should have tools, second (no tool calls) can be anything
        first_call = querier.calls[0]
        assert first_call["tools"] is not None
        assert len(first_call["tools"]) > 0


# ---------------------------------------------------------------------------
# Tests: ToolSolver.solve() — batch + parse feedback
# ---------------------------------------------------------------------------

class TestToolSolverBatch:
    def test_solve_two_problems_parallel(self):
        """Solve two problems in parallel and return correct result list."""
        def make_querier():
            return _StubAPIQuery([
                {"output": r"\boxed{2}", "tool_calls": []},
                {"output": r"\boxed{2}", "tool_calls": []},
            ])

        querier = make_querier()
        solver = ToolSolver(querier=querier, max_tool_rounds=3)
        problems = [_StubProblem(), _StubProblem()]
        results, costs = solver.solve(problems)

        assert len(results) == 2
        assert len(costs) == 2
        for msgs in results:
            assert any(r"\boxed{2}" in m.get("content", "") for m in msgs)

    def test_solve_with_parse_feedback(self):
        """After tool loop, parse feedback sends a correction round."""
        # First call: no tool calls, answer is WRONG (no \boxed{2})
        # Feedback round: corrected answer
        querier = _StubAPIQuery([
            {"output": "The answer is clearly 2.", "tool_calls": []},
            # parse feedback round response
            {"output": r"Corrected: \boxed{2}.", "tool_calls": []},
        ])
        solver = ToolSolver(
            querier=querier,
            max_tool_rounds=3,
            parse_feedback=True,
            max_feedback_rounds=1,
        )
        results, _ = solver.solve([_StubProblem()])
        assert any(r"\boxed{2}" in m.get("content", "") for m in results[0])


# ---------------------------------------------------------------------------
# Tests: _strip_tool_messages
# ---------------------------------------------------------------------------

class TestStripToolMessages:
    def _make_solver(self):
        querier = _StubAPIQuery([])
        return ToolSolver(querier=querier)

    def test_strips_tool_role(self):
        solver = self._make_solver()
        msgs = [
            {"role": "system", "content": "sys"},
            {"role": "user", "content": "q"},
            {"role": "assistant", "content": "thinking", "tool_calls": [{"id": "c1"}]},
            {"role": "tool", "tool_call_id": "c1", "content": '{"ok":true}'},
            {"role": "assistant", "content": r"Answer \boxed{2}."},
        ]
        stripped = solver._strip_tool_messages(msgs)
        roles = [m["role"] for m in stripped]
        assert "tool" not in roles
        assert roles == ["system", "user", "assistant", "assistant"]

    def test_strips_tool_call_assistant_with_no_text(self):
        solver = self._make_solver()
        msgs = [
            {"role": "assistant", "content": "", "tool_calls": [{"id": "c1"}]},
            {"role": "assistant", "content": r"\boxed{2}"},
        ]
        stripped = solver._strip_tool_messages(msgs)
        assert len(stripped) == 1
        assert r"\boxed{2}" in stripped[0]["content"]

    def test_keeps_assistant_text_from_tool_call_message(self):
        solver = self._make_solver()
        msgs = [
            {"role": "assistant", "content": "Let me check.", "tool_calls": [{"id": "c1"}]},
        ]
        stripped = solver._strip_tool_messages(msgs)
        assert len(stripped) == 1
        assert stripped[0]["content"] == "Let me check."
        assert "tool_calls" not in stripped[0]


# ---------------------------------------------------------------------------
# Tests: MATH_TOOLS schema sanity
# ---------------------------------------------------------------------------

class TestMathToolsSchema:
    def test_all_tools_have_required_fields(self):
        for tool in MATH_TOOLS:
            assert tool["type"] == "function"
            fn = tool["function"]
            assert "name" in fn
            assert "description" in fn
            assert "parameters" in fn
            assert "properties" in fn["parameters"]

    def test_tool_names(self):
        names = {t["function"]["name"] for t in MATH_TOOLS}
        assert "calculator" in names
        assert "sympy_tool" in names
        assert "python_tool" in names
        assert "z3_tool" in names
        assert "solve_cnf" in names
        assert "or_tool" in names

    def test_tool_system_prompt_mentions_all_tools(self):
        for tool in MATH_TOOLS:
            name = tool["function"]["name"]
            assert name in TOOL_SYSTEM_PROMPT, f"{name} missing from TOOL_SYSTEM_PROMPT"
