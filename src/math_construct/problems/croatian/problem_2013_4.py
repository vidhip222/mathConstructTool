from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["croatian/problem_2013_4.py"]

import random
from sympy.ntheory import primefactors, factorint, isprime
import math
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.utils import get_latex_array
from math_construct.templates import get_list_template


def get_solution(k: int) -> list[int]:
    res = []
    p = 5
    while len(res) < k:
        if isprime(p):
            res.append(2**(2*p)-1)
        p += 1
    return res

def fastpow(n: int, m: int) -> int:
    """Log n exponentiation of 2^n mod m by squaring"""
    if n == 0:
        return 1
    if n % 2 == 0:
        return fastpow(n//2, m)**2 % m
    return fastpow(n-1, m) * 2 % m


class Problem_HMO_2013_4(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_list_template(),
        parameters=["k"],
        source="HMO 2013 4",
        original_parameters={"k": 10},
        original_solution=get_solution(10),
        problem_url="https://natjecanja.math.hr/wp-content/uploads/2015/02/2013_HMO_rjesenja.pdf#page=14", # page 14
        solution_url="https://natjecanja.math.hr/wp-content/uploads/2015/02/2013_HMO_rjesenja.pdf#page=14", # page 14
        tags=[Tag.NUMBER_THEORY, Tag.FIND_INF, Tag.IS_SIMPLIFIED],
    )
    k: int

    def __init__(self, k: int):
        self.k = k

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(k=self.k)

    def check(self, x: list[int]):
        if len(x) != self.k:
            return False, f"List does not have exactly {self.k} elements", CheckerTag.INCORRECT_LENGTH
        digits = set([len(str(n)) for n in x])
        if len(digits) != self.k:
            return False, f"All elements must have different number of digits", CheckerTag.INCORRECT_SOLUTION
        for n in x:
            if n <= 0:
                return False, f"All elements must be positive", CheckerTag.INCORRECT_FORMAT
            if len(primefactors(n)) <= 2:
                return False, f"{n} does not have more than 2 prime divisors", CheckerTag.INCORRECT_SOLUTION
            if (fastpow(n, n) - 8) % n != 0:
                return False, f"2^n - 8 is not divisible by {n}", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "Problem_HMO_2013_4":
        k = random.randint(7, 15)
        return Problem_HMO_2013_4(k)

    def get_solution(self):
        return get_solution(self.k)
