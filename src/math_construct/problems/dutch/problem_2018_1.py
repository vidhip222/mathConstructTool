from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["dutch/problem_2018_1.py"]

import math
import random
import sympy
from fractions import Fraction
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_list_template
import itertools


def get_solution(n: int) -> list[int]:
    possible_digits = ["4", "8"]
    solutions = []
    for i in itertools.product(possible_digits, repeat=n):
        number = int("".join(i))
        if number % 11 == 0 and number % 3 == 0:
            solutions.append(number)
    return solutions

class ProblemDutch20181(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_list_template(),
        parameters=["n", "k"],
        source="Dutch Math Olympiad Finals 2018 P1",
        problem_url="https://wiskundeolympiade.nl/phocadownload/opgaven/finale/2018/ProblemsKlas6.pdf",
        solution_url="https://wiskundeolympiade.nl/phocadownload/opgaven/finale/2018/Solutions.pdf",
        original_parameters={"n": 10, "k": 50},
        original_solution=get_solution(10),
        tags=[Tag.NUMBER_THEORY, Tag.FIND_ALL, Tag.IS_GENERALIZED, Tag.IS_ORIGINAL] 
    )
    n: int
    k: int

    def __init__(self, n: int, k: int):
        self.n = n
        self.k = k

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(n=self.n, k=self.k)

    def check(self, a: list[int]) -> bool:
        checker_format = self.check_format(a, is_integer=True, expected_length=self.k, is_unique=True)
        if not checker_format[0]:
            return checker_format
        all_solutions = get_solution(self.n)
        for i in a:
            if i not in all_solutions:
                return False, f"{i} is not a shuffle number.", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "ProblemDutch20181":
        n = random.randint(11,20)
        minimal = min(50, len(get_solution(n)))
        k = random.randint(min(5, minimal), minimal)
        return ProblemDutch20181(n, k)
    
    def get_solution(self) -> list[int]:
        return get_solution(self.n)[:self.k]
