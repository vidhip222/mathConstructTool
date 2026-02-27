from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["imc/problem_2012_2.py"]

import random
import numpy as np
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_matrix_template


def get_solution(n: int):
    a = [[0] * n for _ in range(n)]
    for i in range(1, n+1):
        for j in range(1, n+1):
            a[i-1][j-1] = (i-j)**2
    return a


class Problem_IMC_2012_2(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_matrix_template(),
        parameters=["n"],
        source="IMC 2012 P2",
        original_parameters={"n": 7},
        original_solution=get_solution(7),
        problem_url="https://www.imc-math.org.uk/imc2012/IMC2012-day1-questions.pdf",
        solution_url="https://www.imc-math.org.uk/imc2012/IMC2012-day1-solutions.pdf",
        tags=[Tag.ALGEBRA, Tag.FIND_MAX_MIN, Tag.IS_SIMPLIFIED],
    )
    n: int

    def __init__(self, n: int):
        self.n = n

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(n=self.n)

    def check(self, x: list[list[float]]):
        if len(x) != self.n:
            return False, f"The number of rows is not equal to n ({self.n}).", CheckerTag.INCORRECT_LENGTH
        if any(len(row) != self.n for row in x):
            return False, f"The number of columns is not equal to n ({self.n}).", CheckerTag.INCORRECT_LENGTH
        if any(x[i][i] != 0 for i in range(self.n)):
            return False, f"Some diagonal elements are not zero.", CheckerTag.INCORRECT_SOLUTION
        if any(x[i][j] <= 0 for i in range(self.n) for j in range(self.n) if i != j):
            return False, f"Some off-diagonal elements are not positive.", CheckerTag.INCORRECT_SOLUTION
        rank = np.linalg.matrix_rank(x)
        if rank > 3:
            return False, f"The rank is {rank}, which is greater than 3.", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT
        
    @classmethod
    def generate_multiple_explicit(cls, n_problems: int = None) -> list["Problem"]:
        # not used in avg plot
        small = [2,3,4,5,6]
        mid = np.linspace(7, 20, 10).astype(int).tolist()
        big = np.linspace(21, 38, 9).astype(int).tolist() 
        return [cls(n) for n in small + mid + big]

    @staticmethod
    def generate() -> "Problem_IMC_2012_2":
        n = random.randint(6, 20)
        return Problem_IMC_2012_2(n)

    def get_solution(self):
        return get_solution(self.n)
