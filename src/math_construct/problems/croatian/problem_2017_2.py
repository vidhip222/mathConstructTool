from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["croatian/problem_2017_2.py"]

import random
import math
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.utils import get_latex_array
from math_construct.templates import get_list_template


FORMATTING_INSTRUCTIONS = r"""The chessboard is represented as a matrix in LaTeX. 
Present your solution by replacing some empty squares of the chessboard (denoted with "o") with the letters corresponding to the directions of the bishops (A - bishop turned top left, B - bishop turned top right, C - bishop turned bottom right, D - bishop turned bottom left):

$$\begin{array}{cccccccc}
o & o & o & o & o & o & o & o \\
o & o & o & o & o & o & o & o \\
o & o & o & o & o & o & o & o \\
o & o & o & o & o & o & o & o \\
o & o & o & o & o & o & o & o \\
o & o & o & o & o & o & o & o \\
o & o & o & o & o & o & o & o \\
o & o & o & o & o & o & o & o \\
\end{array}$$

Place the whole resulting array inside of $\boxed{...}$.
"""

SOLUTION = [
    "AooooooB",
    "AooABooB",
    "AooDCooB",
    "AooooooB",
    "oooooooo",
    "oooooooo",
    "oooooooo",
    "DDDDCCCC",
]

def get_solution(n: int) -> list[str]:
    return SOLUTION

class Problem_HMO_2017_2(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=FORMATTING_INSTRUCTIONS,
        parameters=["n"],
        source="HMO 2017 2",
        original_parameters={"n": 20},
        original_solution=get_solution(20),
        problem_url="https://natjecanja.math.hr/wp-content/uploads/2015/02/HMO2017-rje.pdf#page=19", # page 19
        solution_url="https://natjecanja.math.hr/wp-content/uploads/2015/02/HMO2017-rje.pdf#page=19", # page 19
        tags=[Tag.COMBINATORICS, Tag.FIND_MAX_MIN, Tag.IS_SIMPLIFIED],
    )
    n: int

    def __init__(self, n: int):
        self.n = n

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(n=self.n)

    def check(self, x: list[str]):
        if len(x) != 8:
            return False, f"List does not have exactly 8 elements", CheckerTag.INCORRECT_LENGTH
        if any(len(row) != 8 for row in x):
            return False, f"All rows must have exactly 8 elements", CheckerTag.INCORRECT_LENGTH
        # count number of bishops
        bishops = "".join(x).count("A") + "".join(x).count("B") + "".join(x).count("C") + "".join(x).count("D")
        if bishops < self.n:
            return False, f"Found {bishops} bishops, but there must be at least {self.n} bishops", CheckerTag.INCORRECT_SOLUTION
        # check if bishops attack each other
        for i in range(8):
            for j in range(8):
                if x[i][j] == "o":
                    continue
                for di, dj in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                    if x[i][j] == "A" and (di, dj) == (1, 1):
                        continue
                    if x[i][j] == "B" and (di, dj) == (1, -1):
                        continue
                    if x[i][j] == "C" and (di, dj) == (-1, -1):
                        continue
                    if x[i][j] == "D" and (di, dj) == (-1, 1):
                        continue
                    for k in range(1, 9):
                        if i+k*di < 0 or i+k*di >= 8 or j+k*dj < 0 or j+k*dj >= 8:
                            break
                        if x[i+k*di][j+k*dj] != "o":
                            return False, f"Bishops {x[i][j]} at ({i}, {j}) and ({i+k*di}, {j+k*dj}) attack each other", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "Problem_HMO_2017_2":
        n = random.randint(16, 20)
        return Problem_HMO_2017_2(n)

    def get_solution(self):
        return get_solution(self.n)
