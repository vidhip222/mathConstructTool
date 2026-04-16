"""
Sanity check for the ReAct tool-calling pipeline.
Tests each component locally without any API calls.

Run: uv run python src/scripts/sanity_check_tool.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

PASS = "\033[92m[PASS]\033[0m"
FAIL = "\033[91m[FAIL]\033[0m"
results = []

def check(name, ok, detail=""):
    tag = PASS if ok else FAIL
    print(f"{tag} {name}" + (f"\n       {detail}" if detail else ""))
    results.append(ok)

# ── 1. Python tool executes code ──────────────────────────────────────────────
print("\n=== 1. Python tool execution ===")
from math_construct.llm.tools.python_tool import PythonTool
tool = PythonTool(timeout=10)

out = tool.run(code="print(2 + 2)")
check("simple arithmetic", out.strip() == "4", f"got: {repr(out)}")

out = tool.run(code="for i in range(3): print(i*i)")
check("loop output", out.strip() == "0\n1\n4", f"got: {repr(out)}")

out = tool.run(code="import sympy; print(sympy.isprime(17))")
check("sympy import", "True" in out, f"got: {repr(out)}")

out = tool.run(code="raise ValueError('oops')")
check("error captured (not crash)", "RuntimeError" in out or "ValueError" in out, f"got: {repr(out)}")

out = tool.run(code="import time; time.sleep(999)")
check("timeout works", "TimeoutError" in out or "Timeout" in out, f"got: {repr(out)}")

# ── 2. Tool registry returns category-aware tools with Python fallback ─────────
print("\n=== 2. Tool registry (category-aware) ===")
from math_construct.llm.tools import get_tools_for_problem
from math_construct.problems import get_all_problem_classes

problems = get_all_problem_classes()
prob_inst = problems[0].generate_multiple(1)[0]
tools = get_tools_for_problem(prob_inst)
tool_names = [t.name for t in tools]
check("at least one tool returned", len(tools) >= 1, f"got {len(tools)} tools: {tool_names}")
check("python fallback available", "run_python" in tool_names, f"got: {tool_names}")
check("no duplicate tools", len(tool_names) == len(set(tool_names)), f"got: {tool_names}")

# ── 3. _parse_action regex ────────────────────────────────────────────────────
print("\n=== 3. Action parser ===")
from math_construct.llm.solvers.react_tool_solver import ReActToolSolver

# Minimal stub so we can instantiate without a real querier
class FakeQuerier:
    kwargs = {}
    def run_queries(self, q): return [], [], {"cost": 0}

solver = ReActToolSolver(querier=FakeQuerier())

sample = """\
Thought: I will brute-force search for the pairs.
Action: run_python
```python
for m in range(2, 15):
    print(m)
```
"""
tool_name, code = solver._parse_action(sample)
check("action name parsed", tool_name == "run_python", f"got: {repr(tool_name)}")
check("code block parsed", "for m in range" in (code or ""), f"got: {repr(code)}")

# No action block
tool_name2, code2 = solver._parse_action("Just reasoning, no action.")
check("no action returns None", tool_name2 is None, f"got: {repr(tool_name2)}")

# ── 4. _has_final_answer ──────────────────────────────────────────────────────
print("\n=== 4. Final answer detection ===")
check("detects boxed",     solver._has_final_answer(r"Final Answer: \boxed{(2,8),(6,48)}"))
check("misses no boxed",   not solver._has_final_answer("I think the answer is 42."))

# ── 5. Stop sequence wiring ───────────────────────────────────────────────────
print("\n=== 5. Stop sequence wiring ===")
class TrackingQuerier:
    kwargs = {}
    calls = []
    def run_queries(self, q):
        self.calls.append(dict(self.kwargs))
        # Return a boxed answer so the loop exits immediately
        return [r"\boxed{done}"], [{"cost": 0.001, "input_tokens": 10, "output_tokens": 5}], {"cost": 0.001}

tq = TrackingQuerier()
solver2 = ReActToolSolver(querier=tq)
solver2.cost = 0
solver2.detailed_cost = [{"cost": 0, "input_tokens": 0, "output_tokens": 0}]

msgs = [{"role": "user", "content": "test"}]
solver2._run_react_loop(prob_inst, msgs, problem_idx=0)

check("stop sequence set during call",
      tq.calls and tq.calls[0].get("stop") == ["Observation:"],
      f"kwargs during call: {tq.calls}")
check("stop sequence removed after call",
      tq.kwargs.get("stop") is None,
      f"kwargs after call: {tq.kwargs}")
check("cost tracked per-problem",
      solver2.detailed_cost[0]["cost"] > 0,
      f"detailed_cost: {solver2.detailed_cost[0]}")

# ── Summary ───────────────────────────────────────────────────────────────────
print(f"\n{'='*45}")
passed = sum(results)
total  = len(results)
color  = "\033[92m" if passed == total else "\033[91m"
print(f"{color}{passed}/{total} checks passed\033[0m")
if passed < total:
    print("Fix failing checks before running the full benchmark.")
    sys.exit(1)
else:
    print("All good — safe to run tool.yaml.")
