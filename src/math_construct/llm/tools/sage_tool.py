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
        "SageMath integrates SymPy, GAP, PARI/GP, Singular, and many other systems. "
        "Best for: algebraic number theory (number fields, ideal class groups), "
        "elliptic curves, modular forms, polynomial arithmetic over arbitrary rings, "
        "advanced combinatorics (matroids, posets, polytopes), "
        "symbolic and numeric computation beyond SymPy's scope. "
        "SageMath syntax is Python with extra mathematical globals pre-loaded. "
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
                                "Complete SageMath code (Python superset with math globals). "
                                "Useful features: number_field(), EllipticCurve(), "
                                "PolynomialRing(), GF(p), Matrix(), Permutations(), "
                                "next_prime(), euler_phi(), continued_fraction(), "
                                "Graph(), Polyhedron(). "
                                "Use print() for output. "
                                "Example — find the class number of Q(sqrt(-23)):\n"
                                "  K = QuadraticField(-23)\n"
                                "  print(K.class_number())\n"
                                "Example — construct the Fano plane incidence matrix:\n"
                                "  D = designs.ProjectiveSpaceBoundedBlock(2, 2)\n"
                                "  print(D.incidence_matrix())"
                            ),
                        }
                    },
                    "required": ["code"],
                },
            },
        }

    def react_prompt_block(self) -> str:
        return """\
### Tool: run_sage
Best for: algebraic number theory (number fields, class groups), elliptic curves,
          modular forms, polynomial arithmetic over arbitrary rings, advanced combinatorics
          (matroids, polytopes), and anything beyond SymPy's scope.
Action label: run_sage
Parameter:
  code (string) — SageMath code (Python superset with math globals). Use print() for output.
Output: stdout from your code, or RuntimeError.

Example:
```python
# Decompose 2025 into sum of four squares
from sage.arith.all import sum_of_squares
print(sum_of_squares(4, 2025, algorithm='pari'))
# Compute the order of element (1 2 3)(4 5) in S5
G = SymmetricGroup(5)
g = G([(1,2,3),(4,5)])
print(g.order())
```
"""

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
