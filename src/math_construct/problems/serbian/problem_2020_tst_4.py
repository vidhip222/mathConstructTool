from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["serbian/problem_2020_tst_4.py"]

import random

from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_list_template
from fractions import Fraction
import numpy as np

FORMATTING_INSTRUCTIONS = r"""Output a comma-separated list of pairs inside of \boxed. For example: \boxed{(\frac{3}{8}, \frac{3}{7}), (\frac{3}{5}, \frac{1}{4})}."""

def get_solution(m: int) -> list[list[Fraction]]:
    # Yes solutions are integers but you don't know that as a contestant
    ret = [] 
    for a in range(1, m+1):
        x = a**(a-1)
        y = a**a 
        ret.append([Fraction(x, 1), Fraction(y, 1)])
    return ret

class ProblemSerbianTst2020_4(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=FORMATTING_INSTRUCTIONS,
        parameters=["m"],
        source="Serbian Team Selection Contest 2020 Problem 4",
        problem_url="https://imomath.com/srb/zadaci/2020_bmo-izborno.pdf",
        solution_url="https://imomath.com/srb/zadaci/2020_bmo-izborno_resenja.pdf#page=3",
        original_parameters={"m": 8}, # reduced from source due to large output size
        original_solution=get_solution(8),
        tags=[Tag.NUMBER_THEORY, Tag.FIND_INF, Tag.IS_SIMPLIFIED, Tag.IS_TRANSLATED]
    )
    m: int 

    def __init__(self, m: int):
        self.m = m

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(m=self.m)
    
    def check(self, solution: list[list[Fraction]]) -> tuple[bool, str, CheckerTag]:
        # length  
        if len(solution) != self.m:
            return False, f"List of size {len(solution)}, should be {self.m}", CheckerTag.INCORRECT_LENGTH
        # uniqueness
        if len(set(tuple(sol) for sol in solution)) != len(solution):
            return False, "All elements should be unique", CheckerTag.INCORRECT_FORMAT

        # format 
        for sol in solution:
            if len(sol) != 2:
                return False, f"Pair {sol} is not of size 2", CheckerTag.INCORRECT_FORMAT
            if sol[0] <= 0 or sol[1] <= 0:
                return False, f"Pair {sol} has non-positive elements", CheckerTag.INCORRECT_FORMAT
        
        # checking is numerically tough, we could try some log magic and worry about numerics
        # or simply check the solution class:
        # x = a^(a-1), y = a^a is the only solution where a is a positive integer  
        for sol in solution:
            # binary search a 
            y = sol[1]
            lo = 1 
            while lo**lo < y:
                lo *= 2
            hi = lo
            lo = max(lo//2, 1)
            while lo < hi:
                mid = (lo + hi) // 2
                if mid**mid < y:
                    lo = mid + 1
                else:
                    hi = mid
            a = lo 
            if a**a != y or a**(a-1) != sol[0]:
                return False, f"Pair {sol} does not satisfy the equation", CheckerTag.INCORRECT_SOLUTION

        return True, "OK", CheckerTag.CORRECT

    @classmethod
    def generate_multiple_explicit(cls, n_problems: int = None) -> list["Problem"]:
        small = [1,2,3,4,5]
        mid = list(range(6, 16))
        big = np.linspace(20, 50, 9).astype(int).tolist()
        return [cls(m) for m in small + mid + big]

    @staticmethod
    def generate() -> "ProblemSerbianTst2020_4":
        m = random.randint(3, 10)
        return ProblemSerbianTst2020_4(m)

    def get_solution(self):
        return get_solution(self.m)
