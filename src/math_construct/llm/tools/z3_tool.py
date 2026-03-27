"""Z3 SMT solver tool.

The LLM writes Python code that uses the `z3-solver` library.
We execute it and return stdout.

Install: pip install z3-solver
"""
from .base_tool import BaseTool

_PREAMBLE = "from z3 import *\n"


class Z3Tool(BaseTool):
    name = "run_z3"
    description = (
        "Execute Python code that uses the Z3 SMT solver (z3-solver library). "
        "Z3 solves systems of constraints over integers, reals, bit-vectors, and booleans. "
        "Best for: number theory (divisibility, modular arithmetic, Diophantine equations), "
        "algebra (polynomial systems), combinatorics (existence of objects with given properties), "
        "and any problem phrased as 'find X satisfying constraints C' or 'prove no X exists'. "
        "The solver returns sat+model (found a solution) or unsat (proved impossible). "
        "Import with: from z3 import *"
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
                                "Python code using z3-solver. "
                                "Key types: Int, Real, Bool, BitVec. "
                                "Key classes: Solver (satisfiability), Optimize (min/max). "
                                "Always call s.check(); if sat, call s.model() to read values. "
                                "Use print() for all output. "
                                "Example — find integers x,y > 0 with x^2 + y^2 = 5*x*y - 3:\n"
                                "  from z3 import *\n"
                                "  x, y = Ints('x y')\n"
                                "  s = Solver()\n"
                                "  s.add(x > 0, y > 0, x**2 + y**2 == 5*x*y - 3)\n"
                                "  if s.check() == sat:\n"
                                "      m = s.model()\n"
                                "      print('x =', m[x], ', y =', m[y])\n"
                                "  else:\n"
                                "      print('No solution')"
                            ),
                        }
                    },
                    "required": ["code"],
                },
            },
        }

    def run(self, code: str) -> str:
        if "from z3" not in code and "import z3" not in code:
            code = _PREAMBLE + code
        return self._run_python_code(code)

    def react_prompt_block(self) -> str:
        return """\
### Tool: run_z3
Best for: number theory (Diophantine equations, modular constraints), algebra (polynomial
          systems over integers/reals), combinatorics (does there exist an object with
          properties P?), or any "find X satisfying constraints" / "prove no X exists" problem.
Action label: run_z3
Parameter:
  code (string) — Python using z3-solver. Types: Int, Real, Bool, BitVec.
                  Call s.check() then s.model() to extract values. Use print() for output.
Output: stdout from your code (model values, sat/unsat), or RuntimeError.

Example:
```python
from z3 import *
# Find positive integers a, b, c < 100 with a^2 + b^2 + c^2 = 2025
a, b, c = Ints('a b c')
s = Solver()
s.add(a > 0, b > 0, c > 0, a < 100, b < 100, c < 100)
s.add(a**2 + b**2 + c**2 == 2025)
if s.check() == sat:
    m = s.model()
    print(m[a], m[b], m[c])
else:
    print("unsat")
```
"""
