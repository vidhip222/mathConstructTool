from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["dutch/problem_2024_2.py"]

import math
import random
import sympy
from fractions import Fraction
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_list_template
import numpy as np  


def get_solution(n):
    steps = [[0,0]]
    if n % 4 != 0:
        steps.extend([[1,1],[2,3],[5,4],[1,5],[0,0]])
    while len(steps) < n:
        l = len(steps)
        steps.extend([[1,l],[2+l,1+l],[3+l,-1],[0,0]])
    return steps

class ProblemDutch20242(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=r"Output the answer as a comma separated list inside of \boxed{...}. For example \boxed{(0,0),(1,0),(1,2),..,(0,0)}. Each point should be in the form $(x, y)$ and indicates the next step in the frog's journey, beginning and ending with (0,0).",
        parameters=["m"],
        source="Dutch Math Olympiad Finals 2024 P2",
        problem_url="https://wiskundeolympiade.nl/phocadownload/opgaven/finale/2024/ProblemsKlas6.pdf",
        solution_url="https://wiskundeolympiade.nl/phocadownload/opgaven/finale/2024/Solutions.pdf",
        original_parameters={"m": 36},
        original_solution=get_solution(36),
        tags=[Tag.IS_SIMPLIFIED, Tag.COMBINATORICS, Tag.FIND_ANY] 
    )
    m: int

    def __init__(self, m: int):
        self.m = m

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(m=self.m)

    def check(self, a: list[list[int]]) -> bool:
        first_point = a[0]
        last_point = a[-1]
        if first_point[0] != 0 or first_point[1] != 0:
            a = [[0, 0]] + a
        if last_point[0] != 0 or last_point[1] != 0:
            a = a + [[0, 0]]
        checker_format = self.check_format(a, is_integer=True, is_matrix=True, expected_length=self.m + 1)
        if not checker_format[0]:
            return checker_format
        
        for i in range(1, len(a)):
            if abs(a[i][0] - a[i-1][0]) == i and abs(a[i][1] - a[i-1][1]) == 1:
                continue
            if abs(a[i][0] - a[i-1][0]) == 1 and abs(a[i][1] - a[i-1][1]) == i:
                continue
            return False, f"Step {i} is invalid. Expected a difference of {i} in one direction and 1 in the other.", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT
        
    @classmethod
    def generate_multiple_explicit(cls, n_problems: int = None) -> list["Problem"]:
        # not used in avg plot
        small = np.linspace(1, 7, 5).astype(int).tolist()
        mid = np.arange(8, 18).tolist()
        big = np.linspace(20, 150, 9).astype(int).tolist() 
        return [cls(4 * k + 1) for k in small + mid + big]

    @staticmethod
    def generate() -> "ProblemDutch20242":
        k = random.randint(7,15)
        if random.random() < 0.5:
            n = 4 * k
        else:
            n = 4 * k + 1
        return ProblemDutch20242(n)
    
    def get_solution(self) -> list[list[int]]:
        return get_solution(self.m)
