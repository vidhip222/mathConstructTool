from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["usamo/problem_2006_2.py"]

import math
import random
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_list_template
import numpy as np

def get_solution(k: int, N: int) -> list[list[int]]:
    return [k*k + k + 1 + i for i in range(-k, k+1)]

class Problem_USAMO_2006_2(Problem):
    """2006 USAMO Problem 2"""
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_list_template(),
        parameters=["k", "N"],
        source="2006 USAMO Problem 2",
        original_parameters={"k": 12, "N": 2*12**3 + 3*12**2 + 3*12},
        original_solution=get_solution(12, 2*12**3 + 3*12**2 + 3*12),
        tags=[Tag.NUMBER_THEORY, Tag.FIND_MAX_MIN, Tag.IS_SIMPLIFIED],
        problem_url="https://artofproblemsolving.com/wiki/index.php/2006_USAMO_Problems/Problem_2",
        solution_url="https://artofproblemsolving.com/wiki/index.php/2006_USAMO_Problems/Problem_2",
    )
    k: int
    N: int

    def __init__(self, k: int, N: int):
        self.k = k
        self.N = N

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(k=self.k, N=self.N)

    def check(self, a: list[int]) -> tuple[bool, str, CheckerTag]:
        if not all(isinstance(y, int) for y in a):
            return False, "All elements should be integers", CheckerTag.INCORRECT_FORMAT
        if len(a) != 2*self.k + 1:
            return False, f"List of size {len(a)}, should be {2*self.k + 1}", CheckerTag.INCORRECT_LENGTH
        if len(set(a)) != 2*self.k + 1:
            return False, f"List should contain {2*self.k + 1} distinct integers", CheckerTag.INCORRECT_FORMAT
        if sum(a) <= self.N:
            return False, f"Sum of the list is {sum(a)}, should be greater than {self.N}", CheckerTag.INCORRECT_SOLUTION
        a = sorted(a)
        if sum(a[-self.k:]) > self.N/2:
            return False, f"Sum of the last {self.k} elements is {sum(a[-self.k:])}, should be at most {self.N/2}", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @classmethod
    def generate_multiple_explicit(cls, n_problems: int = None) -> list["Problem"]:
        small = [2,4,6,8,10]
        mid = np.linspace(11, 31, 10).astype(int).tolist()
        big = np.linspace(50, 350, 9).astype(int).tolist()
        return [cls(k, 2*k**3 + 3*k**2 + 3*k) for k in small + mid + big]

    @staticmethod
    def generate() -> "Problem_USAMO_2006_2":
        k = random.randint(10, 30)
        N = 2*k**3 + 3*k**2 + 3*k
        return Problem_USAMO_2006_2(k, N)

    def get_solution(self):
        return get_solution(self.k, self.N)
