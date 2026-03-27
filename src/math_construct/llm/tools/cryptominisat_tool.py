"""CryptoMiniSat SAT solver tool.

The LLM writes Python code using the `pycryptosat` bindings,
OR writes a DIMACS CNF formula (as a string) that we pass to the solver.

Install: pip install pycryptosat
"""
from .base_tool import BaseTool

_PREAMBLE = "import pycryptosat\n"


class CryptoMiniSatTool(BaseTool):
    name = "run_cryptominisat"
    description = (
        "Execute Python code that uses the CryptoMiniSat SAT solver (pycryptosat library). "
        "SAT solvers decide whether a Boolean formula in CNF (conjunctive normal form) is satisfiable. "
        "Best for: number theory problems encoded as SAT (e.g. primality, XOR constraints, "
        "combinatorial existence via propositional encoding), and problems where "
        "each variable is a Boolean and constraints can be expressed as OR-clauses. "
        "Variables are positive integers; a clause is a list of signed integers "
        "(positive = variable is True, negative = variable is False). "
        "Import with: import pycryptosat"
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
                                "Python code using pycryptosat. "
                                "s = pycryptosat.Solver(). "
                                "s.add_clause([lit1, lit2, ...]): each literal is ±variable_id (1-indexed). "
                                "sat, solution = s.solve(): solution is a list where solution[i] is the "
                                "truth value of variable i+1. "
                                "Use print() for output. "
                                "Example — 3-colouring a triangle (K3) with 3 colours:\n"
                                "  import pycryptosat\n"
                                "  # Variables: x_{v,c} = 1 means vertex v has colour c\n"
                                "  # v in {0,1,2}, c in {0,1,2}, var id = 3*v + c + 1\n"
                                "  def var(v, c): return 3*v + c + 1\n"
                                "  s = pycryptosat.Solver()\n"
                                "  for v in range(3):  # each vertex has at least one colour\n"
                                "      s.add_clause([var(v,0), var(v,1), var(v,2)])\n"
                                "  for u,w in [(0,1),(1,2),(0,2)]:  # adjacent vertices differ\n"
                                "      for c in range(3):\n"
                                "          s.add_clause([-var(u,c), -var(w,c)])\n"
                                "  sat, sol = s.solve()\n"
                                "  print('sat:', sat)\n"
                                "  if sat:\n"
                                "      for v in range(3):\n"
                                "          colour = next(c for c in range(3) if sol[var(v,c)])\n"
                                "          print(f'vertex {v}: colour {colour}')"
                            ),
                        }
                    },
                    "required": ["code"],
                },
            },
        }

    def run(self, code: str) -> str:
        if "import pycryptosat" not in code:
            code = _PREAMBLE + code
        return self._run_python_code(code)

    def react_prompt_block(self) -> str:
        return """\
### Tool: run_cryptominisat
Best for: problems reducible to Boolean SAT — propositional encodings of combinatorics,
          number theory with XOR constraints, or any existence problem with binary variables.
Action label: run_cryptominisat
Parameter:
  code (string) — Python using pycryptosat.
                  Variables are positive integers (1-indexed).
                  add_clause([±var, ...]): positive = True, negative = False.
                  sat, solution = s.solve()  where solution[i] is truth value of variable i+1.
Output: stdout from your code, or RuntimeError.

Example:
```python
import pycryptosat
# Check if x XOR y XOR z = True with x AND y = False
s = pycryptosat.Solver()
s.add_xor_clause([1, 2, 3], True)   # x XOR y XOR z = True
s.add_clause([-1, -2])              # NOT (x AND y)
sat, sol = s.solve()
print("sat:", sat, "solution:", sol[1:4] if sat else "N/A")
```
"""
