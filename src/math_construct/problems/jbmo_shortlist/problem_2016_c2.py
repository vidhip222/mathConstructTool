from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["jbmo_shortlist/problem_2016_c2.py"]

from sympy import isprime
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
import numpy as np
from math_construct.templates import get_list_template
from itertools import combinations


def get_solution() -> list[int]:
    return [i for i in range(1, 51) if i%2==0]

class ProblemJBMO2016C2(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_list_template(),
        parameters=[],
        source="2016 JBMO Shortlist C2",
        original_parameters={},
        original_solution=get_solution(),
        problem_url="https://artofproblemsolving.com/community/c6h1528629p9180554",
        solution_url="https://artofproblemsolving.com/community/c6h1528629p9180554",
        tags=[Tag.NUMBER_THEORY, Tag.FIND_MAX_MIN, Tag.IS_ORIGINAL]
    )

    def __init__(self):
        pass

    def get_problem(self):
        return PROBLEM_TEMPLATE.format()

    def check(self, x: list[int]) -> bool:

        if len(x) != 25:
            return False, f"The count of erased numbers is not the optimal one", CheckerTag.INCORRECT_LENGTH

        for i in x:
            if i > 50 or i < 1:
                return False, f"Numbers should be members of the set $\\{{1,2,\\ldots,50\\}}$", CheckerTag.INCORRECT_FORMAT

        if len(set(x)) != len(x):
            return False, f"Erased numbers are non-distinct", CheckerTag.INCORRECT_FORMAT
        
        

        remaining = set(range(1, 51)) - set(x)
        for n1 in remaining:
            for n2 in remaining:
                if n1 != n2 and isprime(n1+n2):
                    return False, f"The remaining numbers {n1} and {n2}, have a prime sum {n1+n2}", CheckerTag.INCORRECT_SOLUTION

        
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "ProblemJBMO2016C2":
        return ProblemJBMO2016C2()
    
    def get_solution(self):
        return get_solution()
