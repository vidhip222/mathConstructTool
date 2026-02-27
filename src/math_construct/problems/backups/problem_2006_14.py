from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["backups/problem_2006_14.py"]

# https://artofproblemsolving.com/community/c6h238634p1313580
import random
import math
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
import numpy as np
from math_construct.templates import get_list_template
from itertools import combinations


def get_solution(n: int) -> list[int]:
    if n % 2 == 0:
        return [1, n//2 -1, n]
    else:
        return [1, n//2, n-1]

class ProblemJBMO2006P14(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_list_template(),
        parameters=['n'],
        source="2006 JBMO Shortlist 14",
        original_parameters={'n':60},
        original_solution=get_solution(60),
        problem_url="https://artofproblemsolving.com/community/c6h238634p1313580",
        solution_url="https://artofproblemsolving.com/community/c6h238634p1313580",
        tags=[Tag.ALGEBRA, Tag.FIND_ANY, Tag.IS_ORIGINAL]
    )
    n: int

    def __init__(self, n:int):
        self.n = n

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(n=self.n)

    def check(self, x: list[int]) -> bool:
        for i in x:
            if i > self.n or i < 1:
                return False, f"Numbers should be members of the set $\\{{1,2,\\ldots,{self.n}\\}}$", CheckerTag.INCORRECT_FORMAT

        if len(set(x)) != len(x):
            return False, f"Elements of set are non-distinct", CheckerTag.INCORRECT_FORMAT

        remaining = set(range(1, self.n+1)) - set(x)
        if sum(remaining) != math.prod(x):

            return False, f"Partition does not satisfy the required conditions, product of proposed set is {math.prod(x)}, and the sum of the remaining entries is {sum(remaining)}", CheckerTag.INCORRECT_SOLUTION

        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "ProblemJBMO2006P14":
        n = random.randint(20, 60)
        return ProblemJBMO2006P14(n)

    def get_solution(self):
        return get_solution(self.n)
