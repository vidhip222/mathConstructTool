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
        "Execute a MiniZinc constraint programming model (.mzn syntax) and return the solution. "
        "MiniZinc is a high-level declarative language for constraint programming. "
        "Best for: combinatorics puzzles, tiling/covering problems, graph problems, "
        "scheduling, discrete optimisation, and any problem expressible as "
        "'find an assignment of variables from finite domains satisfying constraints'. "
        "Supports solve satisfy (find one solution), solve minimize/maximize (optimise). "
        "Write the full model as a string in MiniZinc syntax."
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
                                "Complete MiniZinc model (.mzn syntax). "
                                "Declare variables as 'var <domain>: <name>;'. "
                                "Add constraints with 'constraint <expr>;'. "
                                "End with 'solve satisfy;' or 'solve minimize <expr>;'. "
                                "Use 'output [show(<var>), ...];' to control output. "
                                "Example — magic square of order 3:\n"
                                "  array[1..3,1..3] of var 1..9: sq;\n"
                                "  constraint alldifferent([sq[i,j] | i,j in 1..3]);\n"
                                "  constraint forall(i in 1..3)("
                                "sum(j in 1..3)(sq[i,j]) = 15);\n"
                                "  constraint forall(j in 1..3)("
                                "sum(i in 1..3)(sq[i,j]) = 15);\n"
                                "  solve satisfy;\n"
                                "  output [show(sq)];"
                            ),
                        },
                        "solver": {
                            "type": "string",
                            "description": "MiniZinc solver backend (default: 'gecode'). Options: gecode, chuffed, coin-bc.",
                            "default": "gecode",
                        },
                    },
                    "required": ["model"],
                },
            },
        }

    def react_prompt_block(self) -> str:
        return """\
### Tool: run_minizinc
Best for: combinatorics puzzles, tiling, covering, graph problems, scheduling,
          any "find an assignment satisfying constraints" problem with finite integer domains.
Action label: run_minizinc
Parameters:
  model  (string) — complete MiniZinc model in .mzn syntax.
  solver (string, optional) — backend solver: gecode (default), chuffed, coin-bc.
Output: solution values as printed by your output statement, or UNSATISFIABLE.

Example:
```
var 1..9: a; var 1..9: b; var 1..9: c;
constraint a != b /\\ b != c /\\ a != c;
constraint a + b + c = 15;
constraint a * b * c = 40;
solve satisfy;
output ["a=", show(a), " b=", show(b), " c=", show(c)];
```
"""

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
