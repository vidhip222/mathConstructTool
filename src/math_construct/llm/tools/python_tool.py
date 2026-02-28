"""General-purpose Python execution tool."""
from .base_tool import BaseTool


class PythonTool(BaseTool):
    name = "run_python"
    description = (
        "Execute arbitrary Python code and return its stdout. "
        "Use for brute-force search, combinatorial enumeration, arithmetic, "
        "or any computation not covered by a specialised solver. "
        "Print ALL results you want to see to stdout. "
        "The tool returns exactly what your code prints."
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
                                "Complete, executable Python code. "
                                "Use print() to output every value you need. "
                                "Standard library and numpy/sympy are available. "
                                "Example — find all n in 1..100 where n | 2^n - 2:\n"
                                "  for n in range(1, 101):\n"
                                "      if (2**n - 2) % n == 0:\n"
                                "          print(n)"
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
### Tool: run_python
Best for: brute-force enumeration, arithmetic, verification of a candidate answer,
          any computation not needing a specialised solver.
Action label: run_python
Parameter:
  code (string) — complete Python code; use print() for all output.
Output: exactly what your code prints to stdout, or a RuntimeError / TimeoutError string.

Example:
```python
# Find all integers k in 1..50 such that k divides C(2k, k)
from math import comb
results = [k for k in range(1, 51) if comb(2*k, k) % k == 0]
print(results)
```
"""
