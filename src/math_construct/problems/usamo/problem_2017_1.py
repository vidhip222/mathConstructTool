from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["usamo/problem_2017_1.py"]

import math
import random
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_list_template


FORMATTING_INSTRUCTIONS = r"""Output your answer as a comma separated list of tuples inside \boxed{...}. For example, if the answer is $(2,3)$ and $(3,5)$, output \boxed{(2,3),(3,5)}."""

def powmod(a, b, mod):
    if b == 0:
        return 1
    if b%2 == 0:
        return powmod(a, b//2, mod)**2 % mod
    return a * powmod(a, b-1, mod) % mod

def get_solution(k: int) -> list[list[int]]:
    res = []
    for n in range(10**8+1, 10**9, 2):
        res.append([n, n+2])
        if len(res) == k:
            return res

class Problem_USAMO_2017_1(Problem):
    """2017 USAMO Problem 1"""
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=FORMATTING_INSTRUCTIONS,
        parameters=["k"],
        source="2017 USAMO Problem 1",
        original_parameters={"k": 10},
        original_solution=get_solution(10),
        problem_url="https://artofproblemsolving.com/wiki/index.php/2017_USAMO_Problems/Problem_1",
        solution_url="https://artofproblemsolving.com/wiki/index.php/2017_USAMO_Problems/Problem_1",
        tags=[Tag.NUMBER_THEORY, Tag.FIND_INF, Tag.IS_SIMPLIFIED],
    )
    k: int

    def __init__(self, k: int):
        self.k = k

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(k=self.k)

    def check(self, x: list[list[int]]) -> tuple[bool, str, CheckerTag]:
        if len(x) != self.k:
            return False, f"List of size {len(x)}, should be {self.k}", CheckerTag.INCORRECT_LENGTH
        # check uniqueness
        if len(set(tuple(xy) for xy in x)) != len(x):
            return False, "All elements should be unique", CheckerTag.INCORRECT_FORMAT
        for a, b in x:
            if a < 10**8 or b < 10**8 or a >= 10**9 or b >= 10**9:
                return False, f"Pair ({a}, {b}) is not in the range [10^8, 10^9]", CheckerTag.INCORRECT_FORMAT
            if math.gcd(a, b) != 1:
                return False, f"Pair ({a}, {b}) is not relatively prime", CheckerTag.INCORRECT_SOLUTION
            if (powmod(a, b, a+b) + powmod(b, a, a+b)) % (a+b) != 0:
                return False, f"For pair ({a}, {b}) the expression a^b + b^a is not divisible by a+b", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "Problem_USAMO_2017_1":
        k = random.randint(30, 100)
        return Problem_USAMO_2017_1(k)

    def get_solution(self):
        return get_solution(self.k)
