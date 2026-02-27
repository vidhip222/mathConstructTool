from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["imo_shortlist/problem_2020_n1.py"]

import math
import random
from fractions import Fraction
from sympy import isprime, mod_inverse
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_list_template


FORMATTING_TEMPLATE = r"""Output the answer as a comma separated list $(p, a_1, a_2, \ldots, a_{k_plus_3})$ inside of $\boxed{{...}}$. For example $\boxed{{17, 1, 2, 3, 4, 5}}$."""

def find_prime(a: list[int]):
    """Find a prime that doesn't divide any of the numbers in a"""
    p = 1
    while True:
        p += 1
        if isprime(p) and all(x % p != 0 for x in a):
            return p

def get_solution(k: int):
    # find 3 primes greater than k
    p, r = k+1, []
    while len(r) < 3:
        if isprime(p):
            r.append(p)
        p += 1
    r += [Fraction(1, r[0]*r[1]*r[2])]
    for i in range(k):
        r += [Fraction(i+2, i+1)*r[i]]

    t = [r[i].denominator for i in range(k+1)]
    for j in range(len(r)):
        for i in range(j):
            t.append(r[j].denominator*r[i].numerator - r[i].denominator*r[j].numerator)
    p = find_prime(t)

    a = [mod_inverse(r[i].denominator, p)*r[i].numerator%p for i in range(k+3)]
    return [p] + a

class Problem_IMOShortlist2020_N1(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=FORMATTING_TEMPLATE,
        parameters=["k"],
        source="IMO Shortlist 2020 N1",
        original_parameters={"k": 10},
        original_solution=get_solution(10),
        problem_url="https://www.imo-official.org/problems/IMO2020SL.pdf#page=72",
        solution_url="https://www.imo-official.org/problems/IMO2020SL.pdf#page=72",
        tags=[Tag.NUMBER_THEORY, Tag.FIND_ANY, Tag.IS_SIMPLIFIED]
    )

    def __init__(self, k: int):
        self.k = k

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(k=self.k)

    def get_formatting_instructions(self):
        return FORMATTING_TEMPLATE.format(k_plus_3=self.k+3)

    def check(self, solution: list[int]) -> bool:
        p, a = solution[0], solution[1:]
        if len(a) != self.k + 3:
            return False, f"List of size {len(a)}, should be {self.k+3}", CheckerTag.INCORRECT_LENGTH
        if not all(isinstance(y, int) for y in a):
            return False, "All elements should be integers", CheckerTag.INCORRECT_FORMAT
        if not isprime(p):
            return False, f"p is not a prime number", CheckerTag.INCORRECT_SOLUTION
        if len(set(a)) != len(a):
            return False, f"a_i are not distinct", CheckerTag.INCORRECT_SOLUTION
        for i in range(len(a)):
            if a[i] < 1 or a[i] >= p:
                return False, f"a_i is not in the range 1 to p-1", CheckerTag.INCORRECT_SOLUTION
        for i in range(self.k):
            if (a[i]*a[i+1]*a[i+2]*a[i+3] - (i+1)) % p != 0:
                return False, f"p does not divide a_ia_{i+1}a_{i+2}a_{i+3} - i", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "Problem_IMOShortlist2020_N1":
        n = random.randint(5, 55)
        return Problem_IMOShortlist2020_N1(n)

    def get_solution(self):
        return get_solution(self.k)
