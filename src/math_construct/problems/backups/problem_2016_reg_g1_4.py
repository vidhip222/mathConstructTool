from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["backups/problem_2016_reg_g1_4.py"]

# https://imomath.com/srb/zadaci/bilten2016.pdf
import random
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
import numpy as np


EXTRA_FORMATTING_INSTRUCTIONS = r"""Output the board where cells are denoted with "1" or "0". Output the answer between \verb|\begin{array}{...}| and \verb|\end{array}| inside of $\boxed{...}$. For example, $\boxed{\begin{array}{ccc}1 & 0 & 0 \\ 0 & 0 & 1 \\ 1 & 1 & 1\end{array}}$."""

def get_solution(N:int) -> list[list[str]]:
    grid = np.zeros((N, N), dtype=int)

    for j in range(N//2):
        grid[2*j, 2*j+1] = 1
    return grid.tolist()

class ProblemSerbianRegional2016_G1_4(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=EXTRA_FORMATTING_INSTRUCTIONS,
        parameters=["N"],
        source="Serbian 2016 Regionals Grade 1 P4",
        original_parameters={"N": 12},
        original_solution=get_solution(12),
        problem_url="https://imomath.com/srb/zadaci/bilten2016.pdf",
        solution_url="https://imomath.com/srb/zadaci/bilten2016.pdf",
        tags=[Tag.COMBINATORICS, Tag.IS_GENERALIZED, Tag.IS_TRANSLATED, Tag.FIND_ANY]
    )

    N: int

    def __init__(self, N):
        self.N = N

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(N=self.N)

    def check(self, x: list[list[str]]) -> bool:
        if len(x) != self.N:
            return False, f"Example should contain {self.N} rows", CheckerTag.INCORRECT_LENGTH
        for row in x:
            if len(row) != self.N:
                return False, f"Each row should be of length {self.N}", CheckerTag.INCORRECT_FORMAT
            
        x = np.array(x)

        if not (abs(np.sum(x, axis=0) - np.sum(x, axis=1))==1).all():
            return False, f"The absolute difference between rows and columns of the same index should equal 1", CheckerTag.INCORRECT_SOLUTION

        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "ProblemSerbianRegional2016_G1_4":
        N = random.randint(5, 8)
        return ProblemSerbianRegional2016_G1_4(N*2)

    def get_solution(self):
        return get_solution(self.N)
