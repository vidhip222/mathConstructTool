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
        "Encode your problem as a SAT formula using clauses (lists of integers). "
        "Useful for number theory problems, combinatorics, and any problem reducible to SAT. "
        "Import with: import pycryptosat. Print your final answer to stdout."
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
                                "Example: import pycryptosat; s = pycryptosat.Solver(); "
                                "s.add_clause([1, 2]); s.add_clause([-1, 3]); "
                                "sat, solution = s.solve(); print(sat, solution)"
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
