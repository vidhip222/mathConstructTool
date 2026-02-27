from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["backups/usamo_problem_1976_1.py"]

import random
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_matrix_template
from math_construct.utils import get_latex_array


EXTRA_FORMATTING_INSTRUCTIONS = r"""Output the board where cells "o" are replaced with "b" or "w", depending on the color:

$${board}$$

Put the answer inside of $\boxed{{...}}$.
"""

class Problem5(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_matrix_template(extra_instructions=EXTRA_FORMATTING_INSTRUCTIONS),
        parameters=["n_rows", "n_cols"],
        source="1976 USAMO Problem 1",
        original_parameters={"n_rows": 4, "n_cols": 6},
        original_solution=["wwbwbb", "wbwbwb", "bwwbbw", "bbbwww"],
        problem_url="https://artofproblemsolving.com/wiki/index.php/1976_USAMO_Problems/Problem_1",
        solution_url="https://artofproblemsolving.com/wiki/index.php/1976_USAMO_Problems/Problem_1",
        tags=[Tag.COMBINATORICS, Tag.IS_GENERALIZED, Tag.IS_ORIGINAL, Tag.FIND_ANY]
    )
    n_rows: int
    n_cols: int

    def __init__(self, n_rows: int, n_cols: int):
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.init_grid = [["o" for _ in range(self.n_cols)] for _ in range(self.n_rows)]

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(n_rows=self.n_rows, n_cols=self.n_cols)

    def get_formatting_instructions(self):
        return EXTRA_FORMATTING_INSTRUCTIONS.format(board=get_latex_array(self.init_grid))

    def check(self, x: list[str]) -> bool:
        if len(x) != self.n_rows:
            return False, f"List of size {len(x)}, should be {self.n_rows}", CheckerTag.INCORRECT_LENGTH
        for row in x:
            if len(row) != self.n_cols:
                return False, f"Row of size {len(row)}, should be {self.n_cols}", CheckerTag.INCORRECT_LENGTH
        if not all(isinstance(y, str) for y in x):
            return False, "All elements should be strings", CheckerTag.INCORRECT_FORMAT
        for i1 in range(self.n_rows):
            for j1 in range(self.n_cols):
                if x[i1][j1] not in ["b", "w"]:
                    return False, f"Cell ({i1}, {j1}) is not black or white", CheckerTag.INCORRECT_FORMAT
                for i2 in range(i1+1, self.n_rows):
                    for j2 in range(j1+1, self.n_cols):
                        if x[i1][j1] == x[i1][j2] == x[i2][j1] == x[i2][j2]:
                            return False, f"All four corners of rectangle ({i1}, {j1}), ({i1}, {j2}), ({i2}, {j1}), ({i2}, {j2}) are the same color", CheckerTag.INCORRECT_SOLUTION
        return True, "OK"

    @staticmethod
    def generate() -> "Problem5":
        n_rows = random.randint(3, 4)
        n_cols = random.randint(5, 6)
        if random.random() < 0.5:
            n_rows, n_cols = n_cols, n_rows
        return Problem5(n_rows, n_cols)

    def get_solution(self):
        mat = self.config.original_solution
        if self.n_rows > self.n_cols:
            mat = ["".join(list(row)) for row in zip(*mat)]
        mat = mat[:self.n_rows]
        mat = [row[:self.n_cols] for row in mat]
        return mat
