"""
Math tools for ToolSolver: calculator, sympy, python, z3, SAT/CNF, OR-Tools.
"""
import ast
import json
import operator
import subprocess
import sys
from typing import Any

# ---------------------------------------------------------------------------
# Tool schemas — OpenAI function-calling format (canonical)
# ---------------------------------------------------------------------------

MATH_TOOLS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Safely evaluate a numeric arithmetic expression and return the result.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Arithmetic expression, e.g. '(12+3)*5 - 8/2' or '2**10'",
                    }
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "sympy_tool",
            "description": (
                "Perform symbolic math using SymPy. "
                "Supported operations: factor, expand, simplify, solve, "
                "gcd, lcm, isprime, factorint, totient, binomial, mod_inverse, "
                "nthroot, floor, ceiling."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": (
                            "One of: factor, expand, simplify, solve, gcd, lcm, "
                            "isprime, factorint, totient, binomial, mod_inverse, nthroot, floor, ceiling"
                        ),
                    },
                    "args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": (
                            "Arguments as strings. Examples: "
                            "gcd→['12','18'], solve→['x**2-4','x'], "
                            "binomial→['10','3'], factorint→['360']"
                        ),
                    },
                },
                "required": ["operation", "args"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "python_tool",
            "description": (
                "Execute short Python code in an isolated subprocess. "
                "sympy, numpy, itertools, math, fractions are available. "
                "Use print() to output results. Good for enumeration, verification, and sequence computation."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to execute. Use print() for all output.",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds (default: 10).",
                    },
                },
                "required": ["code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "z3_tool",
            "description": (
                "Use the Z3 SMT solver via Python code. "
                "Write Python code that imports z3, creates a Solver, adds constraints, calls check(), "
                "and prints 'SAT'/'UNSAT' followed by variable values. "
                "Good for finding integers satisfying arithmetic/modular constraints."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "setup_code": {
                        "type": "string",
                        "description": (
                            "Python code using z3. Example:\n"
                            "s = Solver()\n"
                            "x,y = Ints('x y')\n"
                            "s.add(x+y==10, x>0, y>0)\n"
                            "print('SAT' if s.check()==sat else 'UNSAT')\n"
                            "if s.check()==sat: print(s.model())"
                        ),
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds (default: 10).",
                    },
                },
                "required": ["setup_code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "solve_cnf",
            "description": (
                "Solve a SAT instance in CNF form. Accepts a DIMACS string or a list of clauses. "
                "Literal k means variable x_k is true; -k means x_k is false. "
                "Uses pysat → pycosat → z3 fallback chain."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "cnf": {
                        "oneOf": [
                            {"type": "string"},
                            {
                                "type": "array",
                                "items": {"type": "array", "items": {"type": "integer"}},
                            },
                        ],
                        "description": "DIMACS CNF string OR list-of-clauses, e.g. [[1,2],[-1,3],[-2,-3]]",
                    },
                    "max_var": {
                        "type": "integer",
                        "description": "Largest variable index used (inferred automatically if omitted).",
                    },
                },
                "required": ["cnf"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "or_tool",
            "description": (
                "Use Google OR-Tools CP-SAT solver for combinatorial problems. "
                "Write Python code using ortools.sat.python.cp_model that prints the solution. "
                "Great for Latin squares, graph coloring, scheduling, exact cover."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": (
                            "Python code using cp_model. Example:\n"
                            "model = cp_model.CpModel()\n"
                            "x = model.new_int_var(0,9,'x')\n"
                            "model.add(x > 5)\n"
                            "solver = cp_model.CpSolver()\n"
                            "status = solver.solve(model)\n"
                            "if status == cp_model.FEASIBLE: print(solver.value(x))"
                        ),
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds (default: 15).",
                    },
                },
                "required": ["code"],
            },
        },
    },
]

TOOL_SYSTEM_PROMPT = """\
You have access to computation tools. Follow this strategy to maximise accuracy:

STRATEGY:
1. Use python_tool to SEARCH or BRUTE-FORCE the answer — write a loop that tries candidates and prints the first valid one.
2. ALWAYS verify your candidate answer using python_tool before submitting — run code that checks all required conditions and prints True/False.
3. NEVER submit a guess without first verifying it with a tool. If verification fails, search again.

AVAILABLE TOOLS:
- calculator(expression): Safe arithmetic. e.g. '(n*(n+1))//2'
- sympy_tool(operation, args): Symbolic math — factor, expand, simplify, solve, gcd, lcm, isprime, factorint, totient, binomial, mod_inverse, nthroot, floor, ceiling.
- python_tool(code, timeout?): Run any Python. numpy, sympy, itertools, math, fractions available. Use print() for output. Write PROPER multi-line Python — loops and functions work fine.
- z3_tool(setup_code, timeout?): Z3 SMT solver. Declare Int/Bool vars, add constraints, call check(). Good for finding integers satisfying arithmetic constraints.
- solve_cnf(cnf, max_var?): SAT solver — DIMACS string or list-of-clauses e.g. [[1,2],[-1,3]].
- or_tool(code, timeout?): OR-Tools CP-SAT. Write Python using cp_model. Best for combinatorial search.

EXAMPLE PATTERN (always follow this):
  Step 1 — Search: call python_tool with a brute-force loop that finds a candidate answer.
  Step 2 — Verify: call python_tool again to confirm the candidate satisfies ALL conditions.
  Step 3 — Submit: only then write your final \\boxed{} answer.

IMPORTANT RULES:
- Tool results are intermediate. Your final answer must still be in the required \\boxed{} format.
- If python_tool returns an error, FIX the code and try again — do not fall back to guessing.
- Write complete, self-contained Python code in each call (include all imports).
"""

# ---------------------------------------------------------------------------
# Implementations
# ---------------------------------------------------------------------------

_SAFE_BINOPS: dict = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_SAFE_UNARYOPS: dict = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _safe_calculate(expression: str) -> dict:
    def _eval(node: ast.AST):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _SAFE_BINOPS:
            return _SAFE_BINOPS[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _SAFE_UNARYOPS:
            return _SAFE_UNARYOPS[type(node.op)](_eval(node.operand))
        raise ValueError("Unsupported operation")
    try:
        parsed = ast.parse(expression, mode="eval")
        return {"ok": True, "result": _eval(parsed)}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _sympy_compute(operation: str, args: list) -> dict:
    try:
        from sympy import (
            symbols, sympify, factor, expand, simplify, solve,
            gcd, lcm, isprime, factorint, totient, binomial,
            mod_inverse, Integer, Rational, floor, ceiling, nsimplify,
        )
        op = operation.lower().strip()

        if op == "factor":
            return {"ok": True, "result": str(factor(sympify(args[0])))}
        elif op == "expand":
            return {"ok": True, "result": str(expand(sympify(args[0])))}
        elif op == "simplify":
            return {"ok": True, "result": str(simplify(sympify(args[0])))}
        elif op == "solve":
            var = symbols(args[1]) if len(args) > 1 else symbols("x")
            sol = solve(sympify(args[0]), var)
            return {"ok": True, "result": [str(s) for s in sol]}
        elif op == "gcd":
            return {"ok": True, "result": int(gcd(int(sympify(args[0])), int(sympify(args[1]))))}
        elif op == "lcm":
            return {"ok": True, "result": int(lcm(int(sympify(args[0])), int(sympify(args[1]))))}
        elif op == "isprime":
            return {"ok": True, "result": bool(isprime(int(sympify(args[0]))))}
        elif op == "factorint":
            return {"ok": True, "result": {str(k): v for k, v in factorint(int(sympify(args[0]))).items()}}
        elif op == "totient":
            return {"ok": True, "result": int(totient(int(sympify(args[0]))))}
        elif op == "binomial":
            return {"ok": True, "result": int(binomial(int(sympify(args[0])), int(sympify(args[1]))))}
        elif op == "mod_inverse":
            return {"ok": True, "result": int(mod_inverse(int(sympify(args[0])), int(sympify(args[1]))))}
        elif op == "nthroot":
            n, k = int(sympify(args[0])), int(sympify(args[1]))
            return {"ok": True, "result": str(nsimplify(Integer(n) ** Rational(1, k)))}
        elif op == "floor":
            return {"ok": True, "result": int(floor(sympify(args[0])))}
        elif op == "ceiling":
            return {"ok": True, "result": int(ceiling(sympify(args[0])))}
        else:
            return {
                "ok": False,
                "error": f"Unknown operation '{op}'. Supported: factor, expand, simplify, solve, "
                         "gcd, lcm, isprime, factorint, totient, binomial, mod_inverse, nthroot, floor, ceiling",
            }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _execute_python(code: str, timeout: int = 10) -> dict:
    import tempfile, os
    tmp = None
    try:
        # Write to a temp file so multiline / indented code works correctly
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            tmp = f.name
        result = subprocess.run(
            [sys.executable, tmp],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "ok": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout[:4000],
            "stderr": result.stderr[:2000],
            "timed_out": False,
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "timed_out": True, "error": f"Timed out after {timeout}s"}
    except Exception as e:
        return {"ok": False, "error": str(e)}
    finally:
        if tmp and os.path.exists(tmp):
            try:
                os.unlink(tmp)
            except OSError:
                pass


def _z3_solve(setup_code: str, timeout: int = 10) -> dict:
    if "from z3" not in setup_code and "import z3" not in setup_code:
        setup_code = "from z3 import *\n" + setup_code
    return _execute_python(setup_code, timeout)


def _solve_cnf(cnf: Any, max_var: int = None) -> dict:
    clauses: list[list[int]] = []
    n_vars = max_var

    if isinstance(cnf, list):
        clauses = [list(c) for c in cnf]
        if n_vars is None:
            flat = [abs(lit) for clause in clauses for lit in clause]
            n_vars = max(flat) if flat else 0
    elif isinstance(cnf, str):
        for line in cnf.strip().splitlines():
            line = line.strip()
            if not line or line.startswith(("c", "%")):
                continue
            if line.startswith("p"):
                parts = line.split()
                if len(parts) >= 4:
                    try:
                        n_vars = int(parts[2])
                    except ValueError:
                        pass
                continue
            lits = [int(x) for x in line.split() if x != "0"]
            if lits:
                clauses.append(lits)
        if n_vars is None and clauses:
            n_vars = max(abs(lit) for c in clauses for lit in c)
    else:
        return {"ok": False, "error": "cnf must be a DIMACS string or list of clauses"}

    if not clauses:
        return {"ok": True, "satisfiable": True, "model": [], "solver": "trivial"}

    # pysat
    try:
        from pysat.solvers import Glucose4
        with Glucose4() as solver:
            for clause in clauses:
                solver.add_clause(clause)
            sat = solver.solve()
            model = solver.get_model() if sat else None
        return {"ok": True, "satisfiable": sat, "model": model, "solver": "pysat/Glucose4"}
    except ImportError:
        pass

    # pycosat
    try:
        import pycosat
        result = pycosat.solve(clauses)
        if result == "UNSAT":
            return {"ok": True, "satisfiable": False, "model": None, "solver": "pycosat"}
        if result == "UNKNOWN":
            return {"ok": False, "error": "pycosat returned UNKNOWN"}
        return {"ok": True, "satisfiable": True, "model": list(result), "solver": "pycosat"}
    except ImportError:
        pass

    # z3 fallback
    try:
        import z3
        z3vars: dict = {}
        solver = z3.Solver()
        for clause in clauses:
            lits = []
            for lit in clause:
                v = abs(lit)
                if v not in z3vars:
                    z3vars[v] = z3.Bool(f"x{v}")
                lits.append(z3vars[v] if lit > 0 else z3.Not(z3vars[v]))
            solver.add(z3.Or(*lits))
        check = solver.check()
        if check == z3.sat:
            m = solver.model()
            model = []
            for i in range(1, (n_vars or 0) + 1):
                if i in z3vars:
                    val = m.eval(z3vars[i], model_completion=True)
                    model.append(i if z3.is_true(val) else -i)
            return {"ok": True, "satisfiable": True, "model": model, "solver": "z3"}
        if check == z3.unsat:
            return {"ok": True, "satisfiable": False, "model": None, "solver": "z3"}
        return {"ok": False, "error": "z3 returned unknown"}
    except ImportError:
        pass

    return {"ok": False, "error": "No SAT solver available (install pysat, pycosat, or z3)"}


def _or_solve(code: str, timeout: int = 15) -> dict:
    if "from ortools" not in code and "import ortools" not in code:
        code = "from ortools.sat.python import cp_model\n" + code
    return _execute_python(code, timeout)


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

def dispatch_tool(name: str, arguments: dict) -> dict:
    """Dispatch a tool call by name and return a JSON-serialisable result dict."""
    try:
        if name == "calculator":
            return _safe_calculate(str(arguments.get("expression", "")))
        elif name == "sympy_tool":
            return _sympy_compute(
                str(arguments.get("operation", "")),
                [str(a) for a in arguments.get("args", [])],
            )
        elif name == "python_tool":
            return _execute_python(
                str(arguments.get("code", "")),
                timeout=int(arguments.get("timeout", 10)),
            )
        elif name == "z3_tool":
            return _z3_solve(
                str(arguments.get("setup_code", "")),
                timeout=int(arguments.get("timeout", 10)),
            )
        elif name == "solve_cnf":
            return _solve_cnf(
                arguments.get("cnf"),
                arguments.get("max_var"),
            )
        elif name == "or_tool":
            return _or_solve(
                str(arguments.get("code", "")),
                timeout=int(arguments.get("timeout", 15)),
            )
        else:
            return {"ok": False, "error": f"Unknown tool: {name}"}
    except Exception as e:
        return {"ok": False, "error": f"Tool dispatch error: {e}"}
