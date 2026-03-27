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
        "Check a Lean 4 proof or evaluate a computation. "
        "Best for: formally verifying that a constructed solution satisfies all constraints, "
        "checking decidable propositions (primality, divisibility, inequalities) with 'by decide', "
        "and computing values with #eval (Nat arithmetic, list operations, Fin types). "
        "If the code type-checks without errors, the mathematical statement is formally verified. "
        "Use #eval <expr> to print computed values. "
        "Note: Mathlib is available only if LEAN_PROJECT_DIR is set to a Mathlib project."
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
                                "Lean 4 code to type-check and/or evaluate. "
                                "Use #eval <expr> to print values (Nat, List, Bool, etc.). "
                                "Use 'theorem t : <prop> := by decide' for decidable propositions "
                                "(works for concrete numeric statements). "
                                "No semicolons between top-level commands. "
                                "Example — verify 97 is prime and compute 2^10:\n"
                                "  #eval Nat.Prime 97\n"
                                "  #eval 2^10\n"
                                "Example — check a list is sorted:\n"
                                "  #eval [1,3,5,7,9].Sorted (· ≤ ·)\n"
                                "Example — verify 3^4 + 4^4 + 5^4 = 6^4 + 2^4:\n"
                                "  theorem h : 3^4 + 4^4 + 5^4 = 6^4 + 2^4 := by decide"
                            ),
                        }
                    },
                    "required": ["code"],
                },
            },
        }

    def react_prompt_block(self) -> str:
        return """\
### Tool: run_lean
Best for: formally verifying that a candidate answer satisfies all problem constraints,
          checking concrete arithmetic propositions (primality, divisibility) via 'by decide',
          computing values with #eval.
Action label: run_lean
Parameter:
  code (string) — Lean 4 code. Use #eval to print values; 'theorem t : P := by decide'
                  to formally verify decidable propositions. No semicolons between commands.
Output: stdout from #eval statements, or "proof checked successfully", or LeanError.

Example:
```lean
-- Verify that 3, 4, 5 is a Pythagorean triple
theorem pythagorean : 3^2 + 4^2 = 5^2 := by decide
#eval 3^2 + 4^2   -- prints 25
#eval Nat.Prime 97  -- prints true
```
"""

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
