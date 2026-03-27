"""SymPy symbolic mathematics tool.

The LLM writes Python code using SymPy for symbolic computation.

Install: pip install sympy  (already in pyproject.toml)
"""
from .base_tool import BaseTool

_PREAMBLE = "from sympy import *\n"


class SymPyTool(BaseTool):
    name = "run_sympy"
    description = (
        "Execute Python code that uses SymPy for symbolic mathematics. "
        "Best for: solving polynomial / Diophantine equations symbolically, "
        "number theory (factorisations, primes, totient, modular inverse, continued fractions), "
        "combinatorics (binomial coefficients, partitions, permutations), "
        "symbolic calculus (limits, derivatives, integrals, series), "
        "geometry (distance, intersection, area), and algebraic simplification. "
        "SymPy returns exact symbolic answers (fractions, radicals, etc.) — no floating-point error. "
        "Import with: from sympy import *"
    )

    @property
    def schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": (
                                "Python code using SymPy. "
                                "Key functions: solve(), factor(), expand(), simplify(), "
                                "isprime(), factorint(), totient(), gcd(), lcm(), "
                                "binomial(), nthroot(), Rational(), symbols(), "
                                "diophantine(), solve_congruence(). "
                                "Use print() for output. "
                                "Example — find all integer solutions to x^2 - 2y^2 = 1 with x,y < 100:\n"
                                "  from sympy import *\n"
                                "  x, y = symbols('x y', integer=True)\n"
                                "  sols = [(xv, yv) for xv in range(1,100)\n"
                                "          for yv in range(0,100)\n"
                                "          if xv**2 - 2*yv**2 == 1]\n"
                                "  print(sols)"
                            ),
                        }
                    },
                    "required": ["code"],
                },
            },
        }

    def run(self, code: str) -> str:
        if "from sympy" not in code and "import sympy" not in code:
            code = _PREAMBLE + code
        return self._run_python_code(code)

    def react_prompt_block(self) -> str:
        return """\
### Tool: run_sympy
Best for: symbolic equation solving, number theory (factorisation, totient, primes),
          combinatorics (binomials, partitions), Diophantine equations, algebraic simplification,
          and symbolic geometry. Returns exact answers (no floating-point error).
Action label: run_sympy
Parameter:
  code (string) — Python using SymPy (from sympy import *). Use print() for output.
Output: stdout from your code, or RuntimeError.

Example:
```python
from sympy import *
# Factor 2^64 + 1 and find all prime factors
n = 2**64 + 1
print(factorint(n))
# Solve x^3 - 6x^2 + 11x - 6 = 0 symbolically
x = symbols('x')
print(solve(x**3 - 6*x**2 + 11*x - 6, x))
```
"""
