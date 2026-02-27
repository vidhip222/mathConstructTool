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
        "Use Z3 to encode mathematical constraints as an SMT problem and find satisfying assignments. "
        "Excellent for number theory, algebra, and combinatorics. "
        "Import z3 with: from z3 import *. Print your final answer to stdout."
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
                                "Python code using the z3-solver library. "
                                "Example: from z3 import *; x = Int('x'); s = Solver(); "
                                "s.add(x > 0, x < 10); print(s.check(), s.model())"
                            ),
                        }
                    },
                    "required": ["code"],
                },
            },
        }

    def run(self, code: str) -> str:
        # Prepend z3 import if not present
        if "from z3" not in code and "import z3" not in code:
            code = _PREAMBLE + code
        return self._run_python_code(code)
