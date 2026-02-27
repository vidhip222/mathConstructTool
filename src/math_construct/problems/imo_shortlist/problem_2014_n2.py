from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["imo_shortlist/problem_2014_n2.py"]

# NOTE: Added x<y to force bigger numbers

from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
import itertools
import math
import random
from fractions import Fraction


FORMATTING_INSTRUCTIONS = r"""Output a comma-separated list of pairs (x, y), inside of \boxed, for example \boxed{(2,3), (5,6)}."""

def get_solution(n: int) -> list[list[int]]:
    pairs = []
    for m in range(2, n+2):
        x = m*m*m+m*m-2*m-1
        y = m*m*m+2*m*m-m-1
        pairs.append([x, y])
    return pairs

class Problem2014N2(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=FORMATTING_INSTRUCTIONS,
        parameters=["n"],
        source="IMO 2014 Shortlist N2",
        original_parameters={"n": 25},
        original_solution=get_solution(25),
        problem_url="https://www.imo-official.org/problems/IMO2014SL.pdf#page=72",
        solution_url="https://www.imo-official.org/problems/IMO2014SL.pdf#page=72",
        tags=[Tag.NUMBER_THEORY, Tag.FIND_ALL, Tag.IS_SIMPLIFIED] 
    )
    n: int

    def __init__(self, n: int):
        self.n = n 

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(n=self.n)
    
    def check(self, solution: list[list[int]]) -> tuple[bool, str, CheckerTag]:
        n = self.n
        if len(solution) != n:
            return False, f"List of size {len(solution)}, should be {n}", CheckerTag.INCORRECT_LENGTH
        # assert uniqueness
        if len(set(tuple(xy) for xy in solution)) != len(solution):
            return False, "All elements should be unique", CheckerTag.INCORRECT_FORMAT

        for xy in solution:
            if len(xy) != 2:
                return False, f"List element {xy} is not a pair", CheckerTag.INCORRECT_FORMAT
            if xy[0]<=0 or xy[1]<=0:
                return False, f"Pair {xy} has a non-positive element", CheckerTag.INCORRECT_SOLUTION
            if xy[0] >= xy[1]:
                return False, f"Pair {xy} violates x<y", CheckerTag.INCORRECT_SOLUTION
        
        for x, y in solution:
            lhs = abs(x-y)+1 
            rhs_inner = 7*x*x-13*x*y+7*y*y
            rhs = round(rhs_inner**(1/3))
            if rhs*rhs*rhs != rhs_inner:
                return False, f"Cube root of {rhs_inner} is not an integer", CheckerTag.INCORRECT_SOLUTION
            if lhs != rhs:
                return False, f"Equation is not satisfied for {x}, {y}: {lhs} != {rhs}", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "Problem2014N2":
        n = random.randint(20, 40)
        return Problem2014N2(n)

    def get_solution(self):
        return get_solution(self.n)
