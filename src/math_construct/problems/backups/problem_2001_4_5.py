from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["backups/problem_2001_4_5.py"]

import random
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.utils import get_latex_array


FORMATTING_INSTRUCTIONS = r"""Output the squares by replacing x with a digit from 0 to 9, where cells corresponding to the same digit denote the same square.

$${init_grid}$$

For example, the following grid consists of 6 squares denoted by the digits 0-5:
$$
\begin{{array}}{{ccc}}
0 & 0 & 1 \\
0 & 0 & 2 \\
4 & 5 & 3 \\
\end{{array}}
$$

Output the array inside of $\boxed{{...}}$.
"""

min_sq = [
    [1],
    [2, 1],
    [3, 3, 1],
    [4, 2, 4, 1],
    [5, 4, 4, 5, 1],
    [6, 3, 2, 3, 5, 1],
    [7, 5, 5, 5, 5, 5, 1],
    [8, 4, 5, 2, 5, 4, 7, 1],
    [9, 6, 3, 6, 6, 3, 6, 7, 1],
    [10, 5, 6, 4, 2, 4, 6, 5, 6, 1],
    [11, 7, 6, 6, 6, 6, 6, 6, 7, 6, 1],
    [12, 6, 4, 3, 6, 2, 6, 3, 4, 5, 7, 1],
    [13, 8, 7, 7, 6, 6, 6, 6, 7, 7, 6, 7, 1],
    [14, 7, 7, 5, 7, 5, 2, 5, 7, 5, 7, 5, 7, 1],
    [15, 9, 5, 7, 3, 4, 8, 8, 4, 3, 7, 5, 8, 7, 1],
]

def get_minimum(m: int, n: int) -> int:
    if n > m:
        m, n = n, m
    return min_sq[m-1][n-1]

# solution for 11x13
ORIGINAL_SOLUTION = [
    "0000111122222",
    "0000111122222",
    "0000111122222",
    "0000111122222",
    "3333333422222",
    "3333333555555",
    "3333333555555",
    "3333333555555",
    "3333333555555",
    "3333333555555",
    "3333333555555",
]

class Problem11(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=FORMATTING_INSTRUCTIONS,
        parameters=["m", "n"],
        source="USAMTS 01/02 Round 4 Problem 5",
        original_parameters={"m": 11, "n": 13},
        original_solution=ORIGINAL_SOLUTION,
        problem_url="https://files.usamts.org/Problems_13_4.pdf",
        solution_url="https://files.usamts.org/Solutions_13_4.pdf",
        tag=[Tag.PUZZLE, Tag.IS_ORIGINAL, Tag.IS_GENERALIZED, Tag.FIND_MAX_MIN]
    )
    m: int
    n: int
    init_grid: str

    def __init__(self, m: int, n: int):
        self.m = m
        self.n = n
        self.init_grid = get_latex_array([["x"] * self.n] * self.m)

    def get_problem(self):
        min_sq = get_minimum(self.m, self.n)
        return PROBLEM_TEMPLATE.format(m=self.m, n=self.n, k=min_sq, init_grid=self.init_grid)

    def get_formatting_instructions(self):
        return FORMATTING_INSTRUCTIONS.format(init_grid=self.init_grid)

    def check(self, x: list[str]):
        if len(x) != self.m:
            return False, f"List of size {len(x)}, should be {self.m}", CheckerTag.INCORRECT_LENGTH
        for row in x:
            if len(row) != self.n:
                return False, f"Row of size {len(row)}, should be {self.n}", CheckerTag.INCORRECT_LENGTH
            if not all(c.isdigit() for c in row):
                return False, "Not all cells are digits", CheckerTag.INCORRECT_FORMAT

        coords = {}
        for i, row in enumerate(x):
            for j, c in enumerate(row):
                coords[c] = coords.get(c, []) + [(i, j)]
        if len(coords.keys()) != get_minimum(self.m, self.n):
            return False, "Solution does not use minimum number of squares", CheckerTag.INCORRECT_SOLUTION
        
        # check if all cells from the same digit form a square
        for d in coords.keys():
            # find bottom left
            min_i = min(coords[d], key=lambda x: x[0])[0]
            min_j = min(coords[d], key=lambda x: x[1])[1]
            # find top right
            max_i = max(coords[d], key=lambda x: x[0])[0]
            max_j = max(coords[d], key=lambda x: x[1])[1]
            # check if all cells from the same digit form a square
            for i in range(min_i, max_i+1):
                for j in range(min_j, max_j+1):
                    if (i, j) not in coords[d]:
                        return False, f"Cells of digit {d} do not form a rectangle", CheckerTag.INCORRECT_SOLUTION
            # check if it's a square
            if max_i - min_i != max_j - min_j:
                return False, f"Cells of digit {d} do not form a square", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "Problem11":
        m = random.randint(6, 15)
        n = random.randint(6, 15)
        return Problem11(m, n)
