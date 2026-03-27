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
        "GAP is a computer algebra system specialising in group theory, combinatorics, "
        "number theory, and discrete algebra. "
        "Best for: computing group orders, automorphisms, conjugacy classes, "
        "permutation groups, polynomial rings over finite fields, "
        "number-theoretic functions (Euler phi, Möbius, cyclotomic polynomials), "
        "and combinatorial structures such as Latin squares and block designs. "
        "Use Print() to output results. Always end code with QUIT; to exit cleanly."
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
                                "Complete GAP code. Use Print() (not Display()) for programmatic output. "
                                "Always end with QUIT; "
                                "GAP syntax: := for assignment, -> for function, ; to end statements. "
                                "Example — compute the order of the symmetric group S5 "
                                "and the number of its conjugacy classes:\n"
                                "  g := SymmetricGroup(5);\n"
                                "  Print(Order(g), \"\\n\");\n"
                                "  Print(NrConjugacyClasses(g), \"\\n\");\n"
                                "  QUIT;"
                            ),
                        }
                    },
                    "required": ["code"],
                },
            },
        }

    def react_prompt_block(self) -> str:
        return """\
### Tool: run_gap
Best for: group theory (orders, automorphisms, conjugacy classes), number theory
          (Euler phi, Möbius function, cyclotomic polynomials), combinatorics
          (Latin squares, block designs), polynomial rings over finite fields.
Action label: run_gap
Parameter:
  code (string) — complete GAP code. Use Print() for output. End with QUIT;
Output: stdout from GAP, or RuntimeError (check syntax carefully; GAP is case-sensitive).

Example:
```
# Compute Euler's totient for numbers 1..10
for n in [1..10] do
    Print(n, " -> ", Phi(n), "\n");
od;
QUIT;
```
"""

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
