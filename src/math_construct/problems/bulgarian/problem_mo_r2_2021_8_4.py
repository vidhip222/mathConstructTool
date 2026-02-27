from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["bulgarian/problem_mo_r2_2021_8_4.py"]

from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_integer_template
import numpy as np
import random


def get_solution(k: int) -> list[int]:
    m = max(k - 8, 1)
    return 2**m

def mod_exp(a: int, y: int, p: int) -> int:
    """Computes (a^y) % p using modular exponentiation."""
    result = 1  # Initialize result
    a = a % p   # Reduce a modulo p initially

    while y > 0:
        # If y is odd, multiply the current base with the result
        if y % 2 == 1:
            result = (result * a) % p

        # Square the base and halve the exponent
        a = (a * a) % p
        y //= 2

    return result

class ProblemBulMO2021P8_4(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_integer_template(),
        parameters=["k"],
        source="Bulgarian MO II P8.4",
        original_parameters={"k": 30},
        original_solution=get_solution(30),
        problem_url="https://klasirane.com/competitions/OLI/2-%D0%9E%D0%B1%D0%BB%D0%B0%D1%81%D1%82%D0%B5%D0%BD%20%D0%BA%D1%80%D1%8A%D0%B3",
        solution_url="https://klasirane.com/competitions/OLI/2-%D0%9E%D0%B1%D0%BB%D0%B0%D1%81%D1%82%D0%B5%D0%BD%20%D0%BA%D1%80%D1%8A%D0%B3",
        tags=[Tag.NUMBER_THEORY, Tag.FIND_ANY, Tag.IS_ORIGINAL, Tag.IS_TRANSLATED]
    )
    k: int

    def __init__(self, k: int):
        self.k = k

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(k=self.k)

    def check(self, x: int) -> bool:
        if x <= 0 or type(x) != int:
            return False, f'Answer should be a positive integer', CheckerTag.INCORRECT_FORMAT
        p = 2**self.k
        An = mod_exp(6561, x, p) - 6*mod_exp(729, x, p) - 4*mod_exp(81, x, p) + 2*mod_exp(3, 2*x+3, p) - 45
        if An % p != 0:
            return False, f'Example does not satisfy the answer', CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "ProblemBulMO2021P8_4":
        N = random.randint(30, 80)
        return ProblemBulMO2021P8_4(N)

    def get_solution(self):
        return get_solution(self.k)
