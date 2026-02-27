"""Lean 4 formal proof checking tool.

The LLM writes a Lean 4 proof; we check it with `lake env lean`.
Useful for verifying that a construction satisfies all constraints.

Install: https://leanprover.github.io/lean4/doc/setup.html
         elan (Lean version manager) is recommended.
         A minimal Mathlib project is assumed to be in $LEAN_PROJECT_DIR.
"""
import tempfile
import os
from .base_tool import BaseTool


_LEAN_PROJECT_DIR = os.environ.get("LEAN_PROJECT_DIR", "")


class LeanTool(BaseTool):
    name = "run_lean"
    description = (
        "Check a Lean 4 proof or computation. "
        "Write a Lean 4 snippet that type-checks if and only if the mathematical "
        "statement holds. Use #eval to print computed values. "
        "Useful to formally verify that a constructed solution satisfies all constraints."
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
                                "Lean 4 code to check. "
                                "Example: '#eval Nat.Prime 97' "
                                "or a theorem with 'by decide' for decidable propositions."
                            ),
                        }
                    },
                    "required": ["code"],
                },
            },
        }

    def run(self, code: str) -> str:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".lean", delete=False, encoding="utf-8"
        ) as f:
            f.write(code)
            tmp_path = f.name

        try:
            # If we have a Lean project, run inside it; otherwise use plain lean
            if _LEAN_PROJECT_DIR and os.path.isdir(_LEAN_PROJECT_DIR):
                cmd = ["lake", "env", "lean", tmp_path]
                cwd = _LEAN_PROJECT_DIR
            else:
                cmd = ["lean", tmp_path]
                cwd = None

            try:
                import subprocess
                proc = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    cwd=cwd,
                )
                out = proc.stdout.strip()
                err = proc.stderr.strip()
                if proc.returncode != 0:
                    return f"LeanError:\n{err}" if err else f"Lean exited with code {proc.returncode}"
                return out if out else "Lean: proof checked successfully (no output)"
            except FileNotFoundError:
                return "ToolNotFound: 'lean' is not installed or not on PATH"
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
