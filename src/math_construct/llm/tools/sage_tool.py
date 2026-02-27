"""SageMath tool.

The LLM writes SageMath code; we call `sage -c "..."` or pipe to `sage`.
SageMath subsumes SymPy, GAP, R, and many other systems.

Install: https://www.sagemath.org/  (add `sage` to PATH)
         Or via conda: conda install -c conda-forge sage
"""
import tempfile
import os
from .base_tool import BaseTool


class SageTool(BaseTool):
    name = "run_sage"
    description = (
        "Execute SageMath code for advanced mathematical computation. "
        "SageMath covers algebra, number theory, geometry, combinatorics, and more. "
        "It integrates SymPy, GAP, PARI/GP, and other math systems. "
        "Write complete SageMath code; use print() to output results."
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
                                "SageMath code to execute. "
                                "Example: 'p = next_prime(100); print(p)' "
                                "or 'G = SymmetricGroup(5); print(G.order())'"
                            ),
                        }
                    },
                    "required": ["code"],
                },
            },
        }

    def run(self, code: str) -> str:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".sage", delete=False, encoding="utf-8"
        ) as f:
            f.write(code)
            tmp_path = f.name

        try:
            result = self._run_shell_command(
                ["sage", tmp_path]
            )
            return result
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
