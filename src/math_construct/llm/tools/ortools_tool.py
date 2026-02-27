"""OR-Tools CP-SAT solver tool.

The LLM writes Python code using Google OR-Tools CP-SAT solver.

Install: pip install ortools
"""
from .base_tool import BaseTool


class ORToolsTool(BaseTool):
    name = "run_ortools"
    description = (
        "Execute Python code that uses Google OR-Tools CP-SAT solver. "
        "Ideal for combinatorics, scheduling, and constraint satisfaction problems. "
        "Use the CP-SAT solver to encode constraints and find feasible/optimal solutions. "
        "Import with: from ortools.sat.python import cp_model. Print your final answer to stdout."
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
                                "Example: from ortools.sat.python import cp_model; "
                                "model = cp_model.CpModel(); x = model.new_int_var(0,10,'x'); "
                                "solver = cp_model.CpSolver(); solver.solve(model); print(solver.value(x))"
                            ),
                        }
                    },
                    "required": ["code"],
                },
            },
        }

    def run(self, code: str) -> str:
        return self._run_python_code(code)
