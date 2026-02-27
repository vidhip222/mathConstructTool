from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["backups/problem_2015_4.py"]

import random
import math
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.utils import get_latex_array
from math_construct.templates import get_list_template


FORMATTING_INSTRUCTIONS = r"""Present your answer as \boxed{a, b}, e.g. \boxed{1, 2}."""

def brute_force(n: int) -> list[int]:
    # try one as zero
    for a in range(n):
        if (4*a*a - 1) % n == 0:
            return [a, 0]
    for b in range(n):
        if (9*b*b - 1) % n == 0:
            return [0, b]
    for a in range(1000):
        for b in range(1000):
            if (4*a*a + 9*b*b - 1) % n == 0:
                return [a, b]
    return None

def euclid(a, b):
    """Implements extended Euclidean algorithm"""
    if a == 0:
        return b, 0, 1
    g, x1, y1 = euclid(b % a, a)
    return g, y1 - (b // a) * x1, x1

def get_solution(n: int) -> list[int, int]:
    if n % 2 == 1:
        k = n//2
        return [k, 0]
    elif n % 3 != 0:
        k, r = n//3, n%3
        if r == 2:
            k, r = k+1, -1
        return [0, k]
    else:
        # here n is divisible by 6
        r, s = 0, 0
        while n % (2**(r+1)) == 0:
            r += 1
        while n % (3**(s+1)) == 0:
            s += 1
        m = n//(2**r*3**s)
        _, k, l = euclid(2**r, m * 3**s)
        return [abs(k * 2**(r-1)), abs(m*l * 3**(s-1))]


class Problem_HMO_2015_4(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=FORMATTING_INSTRUCTIONS,
        parameters=["n"],
        source="HMO 2015 4",
        original_parameters={"n": 712998},
        original_solution=get_solution(712998),
        problem_url="https://natjecanja.math.hr/wp-content/uploads/2015/12/2015_HMO_rjesenja.pdf#page=14", # page 14
        solution_url="https://natjecanja.math.hr/wp-content/uploads/2015/12/2015_HMO_rjesenja.pdf#page=14", # page 14
        tags=[Tag.NUMBER_THEORY, Tag.FIND_ANY, Tag.IS_SIMPLIFIED],
    )
    n: int

    def __init__(self, n: int):
        self.n = n

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(n=self.n)

    def check(self, x: list[int]):
        if len(x) != 2:
            return False, f"List does not have exactly 2 elements", CheckerTag.INCORRECT_FORMAT
        a, b = x[0], x[1]
        if a < 0 or b < 0:
            return False, f"All elements must be positive", CheckerTag.INCORRECT_FORMAT
        if (4*a*a + 9*b*b - 1) % self.n != 0:
            return False, f"4a^2 + 9b^2 - 1 is not divisible by {self.n}", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "Problem_HMO_2015_4":
        # with 70% pick n divisible by 6
        if random.random() < 0.7:
            while True:
                n = 6*random.randint(1, 200000)
                if brute_force(n) is None:
                    break
        else:
            while True:
                n = random.randint(2, 1000000)
                if brute_force(n) is None:
                    break
        return Problem_HMO_2015_4(n)

    def get_solution(self):
        return get_solution(self.n)

# while True:
#     problem = Problem_HMO_2015_4.generate()
#     solution = problem.get_solution()
#     bf_solution = brute_force(problem.n)
#     print(problem.n, solution, bf_solution)
#     # assert problem.check_raw(bf_solution)
#     assert bf_solution is None
