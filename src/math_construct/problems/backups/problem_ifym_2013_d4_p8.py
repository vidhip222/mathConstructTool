from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["backups/problem_ifym_2013_d4_p8.py"]

from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_integer_template
import numpy as np
import random
import math


def get_solution(n: int) -> list[int]:
    return int(''.join(['1' for _ in range(n-2)] + ['28']))

class ProblemIFYM_2013_P8_4_8(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_integer_template(),
        parameters=["n"],
        source="IFYM 2013 P8 Day 4",
        original_parameters={"n": 20},
        original_solution=get_solution(20),
        problem_url="https://klasirane.com/competitions/OLI/2-%D0%9E%D0%B1%D0%BB%D0%B0%D1%81%D1%82%D0%B5%D0%BD%20%D0%BA%D1%80%D1%8A%D0%B3",
        solution_url="https://klasirane.com/competitions/OLI/2-%D0%9E%D0%B1%D0%BB%D0%B0%D1%81%D1%82%D0%B5%D0%BD%20%D0%BA%D1%80%D1%8A%D0%B3",
        tags=[Tag.NUMBER_THEORY, Tag.FIND_ANY, Tag.IS_ORIGINAL]
    )
    n: int

    def __init__(self, n: int):
        self.n = n

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(n=self.n)

    def check(self, x: int) -> bool:
        
        if len(str(x)) != self.n:
            return False, f"Example number has {len(str(x))} digits instead of {self.n}", CheckerTag.INCORRECT_LENGTH
        
        if '0' in str(x).strip():
            return False, f"Number should not contain zeroes.", CheckerTag.INCORRECT_SOLUTION
        
        digit_prod = math.prod([int(dig) for dig in str(x)])
        new_num = x + digit_prod

        new_digit_prod = math.prod([int(dig) for dig in str(new_num)])

        if digit_prod != new_digit_prod:
            return False, f"Number should have the same digit product", CheckerTag.INCORRECT_SOLUTION

        return True, "OK", CheckerTag.CORRECT
        
    @staticmethod
    def generate() -> "ProblemIFYM_2013_P8_4_8":
        n = random.randint(10, 100)
        return ProblemIFYM_2013_P8_4_8(n)

    def get_solution(self):
        return get_solution(self.n)
