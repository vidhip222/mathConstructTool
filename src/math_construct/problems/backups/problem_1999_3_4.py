from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["backups/problem_1999_3_4.py"]

import math
import random

from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_list_template


def is_square(n: int) -> bool:
    return int(n**0.5)**2 == n

def triangle_area(a: list[int], b: list[int], c: list[int]) -> int:
    return abs(a[0]*b[1] + b[0]*c[1] + c[0]*a[1] - a[1]*b[0] - b[1]*c[0] - c[1]*a[0])

def get_solution(p: int) -> list[list[int]]:
    cand = []
    for x in range(-20, 20):
        for y in range(-20, 20):
            if not is_square(x**2 + y**2):
                continue
            cand += [[x, y]]
    ps = []
    for c1 in cand:
        for c2 in cand:
            if c1 == c2:
                continue
            d2 = (c1[0] - c2[0])**2 + (c1[1] - c2[1])**2
            if not is_square(d2):
                continue
            if triangle_area(c1, c2, [0, 0]) == 0:
                continue
            tp = int(d2**0.5) + (c1[0]**2 + c1[1]**2)**0.5 + (c2[0]**2 + c2[1]**2)**0.5
            if int(tp) == p:
                return [[0, 0], c1, c2]
    return []

class Problem8(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_list_template(
            extra_instructions="Each element of the list should be a pair of integers, e.g. (1, 2)."
        ),
        parameters=["p"],
        source="USAMTS 99/00 Round 3",
        original_parameters={"p": 42},
        original_solution=[[0, 0], [14, 0], [9, 12]],
        problem_url="https://files.usamts.org/Problems_11_3.pdf",
        solution_url="https://files.usamts.org/Solutions_11_3.pdf",
        tag=[Tag.GEOMETRY, Tag.IS_ORIGINAL, Tag.IS_GENERALIZED, Tag.FIND_ANY]
    )
    p: int

    def __init__(self, p: int):
        self.p = p

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(p=self.p)

    def check(self, x: list[list[int]]):
        for p in x:
            if len(p) != 2:
                return False, f"List of size {len(p)}, should be 2", CheckerTag.INCORRECT_LENGTH
            if type(p[0]) != int or type(p[1]) != int:
                return False, "Not all coordinates are integers", CheckerTag.INCORRECT_FORMAT
        tp = 0
        for i in range(3):
            for j in range(i+1, 3):
                d2 = (x[i][0] - x[j][0])**2 + (x[i][1] - x[j][1])**2
                if not is_square(d2):
                    return False, f"Distance between {x[i]} and {x[j]} is not a square", CheckerTag.INCORRECT_SOLUTION
                tp += int(d2**0.5)
        return tp == self.p, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "Problem8":
        cand = []
        for x in range(-20, 20):
            for y in range(-20, 20):
                if not is_square(x**2 + y**2):
                    continue
                cand += [[x, y]]
        ps = []
        for c1 in cand:
            for c2 in cand:
                if c1 == c2:
                    continue
                d2 = (c1[0] - c2[0])**2 + (c1[1] - c2[1])**2
                if not is_square(d2):
                    continue
                if triangle_area(c1, c2, [0, 0]) == 0:
                    continue
                p = int(d2**0.5) + (c1[0]**2 + c1[1]**2)**0.5 + (c2[0]**2 + c2[1]**2)**0.5
                assert p.is_integer()
                if int(p) not in ps:
                    ps += [int(p)]
        return Problem8(random.choice(ps))

    def get_solution(self) -> list[list[int]]:
        return get_solution(self.p)
