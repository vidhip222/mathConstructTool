"""OR-Tools CP-SAT solver tool.

The LLM writes Python code using Google OR-Tools CP-SAT solver.

Install: pip install ortools
"""
from .base_tool import BaseTool


class ORToolsTool(BaseTool):
    name = "run_ortools"
    description = (
        "Execute Python code that uses Google OR-Tools CP-SAT solver. "
        "CP-SAT is a highly efficient constraint programming solver. "
        "Best for: combinatorics (coloring, covering, packing), scheduling, "
        "Latin squares, combinatorial designs, optimization over finite integer domains, "
        "and any problem where variables take integer values with hard constraints. "
        "It handles maximization/minimization natively and scales to large problems. "
        "Import with: from ortools.sat.python import cp_model"
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
                                "Python code using ortools.sat.python.cp_model. "
                                "Steps: (1) create CpModel, (2) add integer variables with "
                                "new_int_var(lb, ub, name), (3) add constraints, "
                                "(4) optionally set objective with minimize/maximize, "
                                "(5) create CpSolver, call solve(model), "
                                "(6) check status == OPTIMAL or FEASIBLE, "
                                "(7) read values with solver.value(var). "
                                "Use print() for output. "
                                "Example — 4-colour a cycle of 6 nodes with at most 3 colours:\n"
                                "  from ortools.sat.python import cp_model\n"
                                "  model = cp_model.CpModel()\n"
                                "  n, k = 6, 3\n"
                                "  c = [model.new_int_var(0, k-1, f'c{i}') for i in range(n)]\n"
                                "  for i in range(n):\n"
                                "      model.add(c[i] != c[(i+1) % n])\n"
                                "  solver = cp_model.CpSolver()\n"
                                "  status = solver.solve(model)\n"
                                "  if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):\n"
                                "      print([solver.value(c[i]) for i in range(n)])"
                            ),
                        }
                    },
                    "required": ["code"],
                },
            },
        }

    def run(self, code: str) -> str:
        return self._run_python_code(code)

    def react_prompt_block(self) -> str:
        return """\
### Tool: run_ortools
Best for: combinatorics (graph colouring, covering, Latin squares, combinatorial designs),
          discrete optimisation, scheduling, and any integer constraint satisfaction at scale.
Action label: run_ortools
Parameter:
  code (string) — Python using ortools.sat.python.cp_model.
                  Create CpModel → add vars (new_int_var) → add constraints →
                  CpSolver().solve(model) → check OPTIMAL/FEASIBLE → solver.value(var).
Output: stdout from your code, or RuntimeError.

Example:
```python
from ortools.sat.python import cp_model
# Place 8 non-attacking rooks on an 8x8 board (one per row and column)
model = cp_model.CpModel()
n = 8
cols = [model.new_int_var(0, n - 1, f'col{i}') for i in range(n)]
model.add_all_different(cols)
solver = cp_model.CpSolver()
if solver.solve(model) in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    print([solver.value(cols[i]) for i in range(n)])
```
"""
