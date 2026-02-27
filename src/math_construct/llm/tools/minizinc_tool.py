"""MiniZinc constraint programming tool.

The LLM writes a MiniZinc model (as a string), we write it to a temp file
and call `minizinc --solver Gecode` (or the default solver).

Install: https://www.minizinc.org/software.html  (add `minizinc` to PATH)
Python bridge: pip install minizinc
"""
import tempfile
import os
from .base_tool import BaseTool


class MiniZincTool(BaseTool):
    name = "run_minizinc"
    description = (
        "Execute a MiniZinc constraint model and return the solution. "
        "MiniZinc is a high-level constraint programming language. "
        "Ideal for combinatorics, puzzles, and discrete optimization. "
        "Write the full .mzn model as a string. Results are printed to stdout."
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
                        "model": {
                            "type": "string",
                            "description": (
                                "A complete MiniZinc model (.mzn syntax). "
                                "Example: 'var 1..10: x; var 1..10: y; "
                                "constraint x + y = 15; solve satisfy; "
                                "output [show(x), \" \", show(y)];'"
                            ),
                        },
                        "solver": {
                            "type": "string",
                            "description": "MiniZinc solver to use (default: 'gecode'). Options: gecode, coin-bc, chuffed.",
                            "default": "gecode",
                        },
                    },
                    "required": ["model"],
                },
            },
        }

    def run(self, model: str, solver: str = "gecode") -> str:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".mzn", delete=False, encoding="utf-8"
        ) as f:
            f.write(model)
            tmp_path = f.name

        try:
            result = self._run_shell_command(
                ["minizinc", "--solver", solver, "--time-limit", str(self.timeout * 1000), tmp_path]
            )
            return result
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
