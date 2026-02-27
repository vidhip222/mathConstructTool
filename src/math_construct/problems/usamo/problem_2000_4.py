from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["usamo/problem_2000_4.py"]

import random
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.utils import get_latex_array
from math_construct.templates import get_matrix_template


EXTRA_FORMATTING_INSTRUCTIONS = r"""Output the chessboard where empty cells "o" are replaced with colored cells "x":

$${init_chessboard}$$
"""

def get_solution(n: int, k: int) -> str:
    ret = ["o"*n for _ in range(n)]
    cells = [(0, j) for j in range(1, n)] + [(i, 0) for i in range(1, n)]
    cells = cells[:k]
    for i in range(n):
        for j in range(n):
            if (i, j) in cells:
                ret[i] = ret[i][:j] + "x" + ret[i][j+1:]
    return ret
    

class Problem14(Problem):
    """2000 USAMO Problem 4"""
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_matrix_template(extra_instructions=EXTRA_FORMATTING_INSTRUCTIONS),
        parameters=["n", "k"],
        source="2000 USAMO Problem 4",
        original_parameters={"n": 10, "k": 18},
        original_solution=get_solution(10, 18),
        problem_url="https://artofproblemsolving.com/wiki/index.php/2000_USAMO_Problems/Problem_4",
        solution_url="https://artofproblemsolving.com/wiki/index.php/2000_USAMO_Problems/Problem_4",
        tags=[Tag.COMBINATORICS, Tag.IS_GENERALIZED, Tag.FIND_MAX_MIN],
    )
    n: int
    k: int

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(n=self.n, k=self.k, init_chessboard=get_latex_array(self.init_chessboard))

    def get_formatting_instructions(self):
        return get_matrix_template(extra_instructions=EXTRA_FORMATTING_INSTRUCTIONS.format(init_chessboard=get_latex_array(self.init_chessboard)))

    def __init__(self, n: int, k: int):
        self.n = n
        self.k = k
        self.init_chessboard = ["o"*n for _ in range(n)]

    def check(self, x: list[str]) -> bool:
        if len(x) != self.n:
            return False, f"List of size {len(x)}, should be {self.n}", CheckerTag.INCORRECT_LENGTH
        if not all(isinstance(y, str) for y in x):
            return False, "All elements should be strings", CheckerTag.INCORRECT_FORMAT
        tot_x = 0
        for i in range(self.n):
            for j in range(self.n):
                if x[i][j] != "x":
                    continue
                tot_x += 1
                found_row, found_col = False, False
                for i2 in range(self.n):
                    if i2 != i and x[i2][j] == "x":
                        found_row = True
                    if i2 != j and x[i][i2] == "x":
                        found_col = True
                if found_row and found_col:
                    return False, f"Found triangle formed by row {i} and column {j}", CheckerTag.INCORRECT_SOLUTION
        if tot_x != self.k:
            return False, f"Total number of x's is {tot_x}, should be {self.k}", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT
    
    @staticmethod
    def generate() -> "Problem14":
        n = random.randint(10, 30)
        k = random.randint(2*n-4, 2*n-2)
        return Problem14(n, k)

    def get_solution(self):
        return get_solution(self.n, self.k)
