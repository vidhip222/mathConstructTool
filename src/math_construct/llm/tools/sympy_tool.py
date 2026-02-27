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
        "Use SymPy for: symbolic algebra, solving equations, number theory (primes, divisors, "
        "modular arithmetic), calculus, combinatorics, and geometry. "
        "Import with: from sympy import *. Print your final answer to stdout."
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
                                "Example: from sympy import *; x = symbols('x'); "
                                "sols = solve(x**2 - x - 6, x); print(sols)"
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
