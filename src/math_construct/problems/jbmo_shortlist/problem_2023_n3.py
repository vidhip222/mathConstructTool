from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["jbmo_shortlist/problem_2023_n3.py"]

import random
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
import numpy as np
from math_construct.templates import get_list_template


def get_solution() -> list[int]:
    return [1, 11, 3, 22, 5, 33, 7, 44, 9, 55, 92, 66, 94, 77, 88, 89, 99]

class ProblemJBMO2023N5(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_list_template(),
        parameters=[],
        source="2023 JBMO Shortlist N5",
        original_parameters={},
        original_solution=get_solution(),
        problem_url="https://artofproblemsolving.com/community/c6h3347830p31039822",
        solution_url="https://artofproblemsolving.com/community/c6h3347830p31039822",
        tags=[Tag.IS_ORIGINAL, Tag.NUMBER_THEORY, Tag.FIND_ANY]
    )
    N: int

    def __init__(self):
        pass

    def get_problem(self):
        return PROBLEM_TEMPLATE.format()

    def check(self, x: list[int]) -> bool:
        if len(x) != 17:
            return False, f"Correct number of entries is 17, got {len(x)}", CheckerTag.INCORRECT_LENGTH
        # check uniqueness
        if len(set(x)) != len(x):
            return False, "All elements should be unique", CheckerTag.INCORRECT_FORMAT
        for i in x:
            if i < 1 or i > 100:
                return False, f"Found number ${i}\\notin A$", CheckerTag.INCORRECT_FORMAT
            for j in x:
                if sum(list(map(int, str(i)))) % sum(list(map(int, str(j)))) == 0 and i%j != 0:
                    return False, f"{sum(list(map(int, str(j))))} divides {sum(list(map(int, str(i))))} but {j} does not divide {i}", CheckerTag.INCORRECT_SOLUTION
                if sum(list(map(int, str(i)))) % sum(list(map(int, str(j)))) != 0 and i%j == 0:
                    return False, f"{j} divides {i} but {sum(list(map(int, str(j))))} does not divide {sum(list(map(int, str(i))))}", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "ProblemJBMO2023N5":
        return ProblemJBMO2023N5()

    def get_solution(self):
        return get_solution()
