"""GAP (Groups, Algorithms, Programming) system tool.

The LLM writes GAP code; we pipe it to the `gap` binary.

Install: https://www.gap-system.org/  (add `gap` to PATH)
"""
import tempfile
import os
from .base_tool import BaseTool


class GAPTool(BaseTool):
    name = "run_gap"
    description = (
        "Execute GAP (Groups, Algorithms, Programming) code. "
        "GAP is a computer algebra system specializing in group theory, "
        "number theory, combinatorics, and discrete algebra. "
        "Write complete GAP code; use Print() to output results. "
        "End your code with QUIT; to exit cleanly."
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
                                "GAP code to execute. "
                                "Example: 'g := Group((1,2,3),(1,2)); Print(Order(g)); Print(\"\\n\"); QUIT;'"
                            ),
                        }
                    },
                    "required": ["code"],
                },
            },
        }

    def run(self, code: str) -> str:
        # Ensure code ends with QUIT;
        stripped = code.strip()
        if not stripped.endswith("QUIT;"):
            code = stripped + "\nQUIT;\n"

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".g", delete=False, encoding="utf-8"
        ) as f:
            f.write(code)
            tmp_path = f.name

        try:
            # -q: quiet (no banner), --nointeract: non-interactive mode
            result = self._run_shell_command(
                ["gap", "-q", "--nointeract", tmp_path]
            )
            return result
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
