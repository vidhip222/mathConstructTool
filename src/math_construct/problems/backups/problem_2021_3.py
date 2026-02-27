from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["backups/problem_2021_3.py"]

import math
import random
import sympy
from fractions import Fraction
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_list_template


def get_solution(n: int):
    directions_mod_8 = [1,1,-1,-1,-1,-1,1,1]
    directions_mod_7 = [1,-1,-1,-1,-1,1,1]
    steps = [[0,0]]
    for i in range(1, n + 1):
        if n % 8 != 0 and i < 8:
            current_dir = directions_mod_7[(i - 1) % 8]
        elif n % 8 == 0:
            current_dir = directions_mod_8[(i - 1) % 8]
        else:
            current_dir = directions_mod_8[i % 8]
        if i % 2 == 1:
            steps.append([steps[-1][0] + i * current_dir, steps[-1][1]])
        else:
            steps.append([steps[-1][0], steps[-1][1] + i * current_dir])
    return steps

class ProblemDutch20213(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=r"Output the answer as comma separated list inside of \boxed{...}. For example \boxed{(0,0),(1,0),(1,2),..,(0,0)}. Each point should be in the form $(x, y)$ and indicates the next step in the frog's journey, beginning and ending with (0,0).",
        parameters=["n"],
        source="Dutch Math Olympiad Finals 2021 P3",
        problem_url="https://wiskundeolympiade.nl/phocadownload/opgaven/finale/2021/ProblemsKlas6.pdf",
        solution_url="https://wiskundeolympiade.nl/phocadownload/opgaven/finale/2021/Solutions.pdf",
        original_parameters={"n": 32},
        original_solution=get_solution(32),
        tags=[Tag.IS_SIMPLIFIED, Tag.FIND_ANY, Tag.COMBINATORICS] 
    )
    n: int

    def __init__(self, n: int):
        self.n = n

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(n=self.n)

    def check(self, a: list[list[int]]) -> bool:
        first_point = a[0]
        last_point = a[-1]
        if first_point[0] != 0 or first_point[1] != 0:
            a = [[0, 0]] + a
        if last_point[0] != 0 or last_point[1] != 0:
            a = a + [[0, 0]]
        
        check_format = self.check_format(a, is_integer=True, is_matrix=True, expected_length=self.n + 1)
        if not check_format[0]:
            return check_format
        for i in range(1, len(a)):
            if i % 2 == 1:
                if a[i][1] != a[i-1][1] or abs(a[i][0] - a[i-1][0]) != i:
                    return False, f"Step {i} is invalid. Expected no difference in the second entry and a difference of {i} in the other.", CheckerTag.INCORRECT_SOLUTION
            else:
                if a[i][0] != a[i-1][0] or abs(a[i][1] - a[i-1][1]) != i:
                    return False, f"Step {i} is invalid. Expected no difference in the first entry and a difference of {i} in the other.", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT
        
    @staticmethod
    def generate() -> "ProblemDutch20213":
        k = random.randint(4,7)
        if random.random() < 0.5:
            n = 8 * k
        else:
            n = 8 * k - 1
        return ProblemDutch20213(n)
    
    def get_solution(self) -> list[list[int]]:
        return get_solution(self.n)
