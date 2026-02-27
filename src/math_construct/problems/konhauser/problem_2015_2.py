from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["konhauser/problem_2015_2.py"]

import math
import random
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag


FORMATTING_TEMPLATE = r"""Output the answer as a comma separated list inside of $\boxed{...}$. For example $\boxed{1.12, 2.13, 3.14}$. You can use real values or valid LaTeX expressions to represent the numbers."""

def get_solution(l):
    quadratic = (1 / 4, - l + l / 2 - 1, (l / 2 - 1) ** 2)
    D = quadratic[1] ** 2 - 4 * quadratic[0] * quadratic[2]
    f_n = (-quadratic[1] + math.sqrt(D)) / (2 * quadratic[0])
    f_n_2 = (-quadratic[1] - math.sqrt(D)) / (2 * quadratic[0])
    return [f_n, f_n_2]


class ProblemKonhauser20152(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=FORMATTING_TEMPLATE,
        problem_url="https://www.macalester.edu/mscs/wp-content/uploads/sites/591/2016/03/Konhauser2015.pdf#page=1",
        solution_url="https://www.macalester.edu/mscs/wp-content/uploads/sites/591/2016/03/Konhauser2015.pdf#page=3",
        parameters=["k", "n", "m", "l"],
        source="Konhauser Problemfest 2015 P2",
        original_parameters={"k": 3, "n": 7, "m": 5, "l": 25},
        original_solution=get_solution(25),
        tags=[Tag.ALGEBRA, Tag.FIND_ALL, Tag.IS_ORIGINAL, Tag.IS_GENERALIZED]
    )
    k: int
    n: int
    m: float
    l: int

    def __init__(self, k: int, n: int, m: float, l: int):
        self.k = k
        self.n = n
        self.m = m
        self.l = l

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(k=self.k, n=self.n, m=self.m, l=self.l)

    def check(self, sol: list[float]) -> bool:
        checker_format = self.check_format(sol, expected_length=2, is_unique=True)
        if not checker_format[0]:
            return checker_format
        for f_n in sol:
            f_m_linear = (f_n + self.l) / 2
            f_m_exp = (self.l * f_n) ** (1 / 2)
            if not (0.999 < abs(f_m_linear - f_m_exp) < 1.001):
                return False, f"Linear function {f_m_linear} is not 1 away from exponential function {f_m_exp} for {f_n}.", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT
        
    @staticmethod
    def generate() -> "ProblemKonhauser20152":
        n = random.randint(2, 100)
        if n <= 3:
            k = 1
        else:
            k = random.randint(3, n)
        if k == n:
            k = k - 1
        l = random.randint(5, 150)
        return ProblemKonhauser20152(k=k, n=n, m=(k + n) / 2, l=l)
    
    def get_solution(self):
        return get_solution(self.l)
