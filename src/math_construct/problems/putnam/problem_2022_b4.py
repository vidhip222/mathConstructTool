from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["putnam/problem_2022_b4.py"]

import math
import random
from fractions import Fraction

from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_list_template


def get_solution(n: int) -> list[float]:
    assert n%3 == 0
    k = n//3-1
    res = [4*i for i in range(k+1)]
    res += [4*k-2, 4*k-1, 4*k-3]
    while res[-1] > 1:
        res += [res[-1]-2]
    res += [2]
    return res



class Problem_Putnam2022B4(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_list_template(),
        parameters=["n"],
        source="Putnam 2022 B4",
        original_parameters={"n": 21},
        original_solution=get_solution(21),
        tags=[Tag.NUMBER_THEORY, Tag.FIND_ANY, Tag.IS_SIMPLIFIED],
        problem_url="https://kskedlaya.org/putnam-archive/2022.pdf",
        solution_url="https://kskedlaya.org/putnam-archive/2022s.pdf",
    )
    n: int

    def __init__(self, n: int):
        self.n = n

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(n=self.n)

    def check(self, x: list[float]):
        def is_arith(arr):
            assert len(arr) == 3
            arr = sorted(arr)
            d1, d2 = arr[1]-arr[0], arr[2]-arr[1]
            return abs(d1-d2) < 1e-3
        if len(x) != self.n:
            return False, f"List of size {len(x)}, should be {self.n}", CheckerTag.INCORRECT_LENGTH
        for i in range(self.n):
            for j in range(i+1, self.n):
                if abs(x[i]-x[j]) < 1e-3:
                    return False, f"Found duplicate {x[i]} at indices {i} and {j}", CheckerTag.INCORRECT_SOLUTION
        x = x + x
        for i in range(self.n):
            if not is_arith(x[i:i+3]):
                return False, "Not an arithmetic progression", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "Problem_Putnam2022B4":
        n = random.randint(3, 12)
        return Problem_Putnam2022B4(3*n)

    def get_solution(self):
        return get_solution(self.n)
