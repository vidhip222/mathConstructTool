from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["backups/problem_2011_3.py"]

import math
import random
import sympy
from fractions import Fraction
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_matrix_template
import itertools


class ProblemDutch20113(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_matrix_template("The element in the $i$-th row and $j$-th column should be 3 if team $i$ won against team $j$, 0 if team $i$ lost against team $j$, and 1 if the game was a draw. The diagonal should be 0."),
        parameters=["n"],
        source="Dutch Math Olympiad Finals 2011 P3",
        original_parameters={"n": 6},
        problem_url="https://wiskundeolympiade.nl/files/opgaven/finale/2011/opgaven_en.pdf",
        solution_url="https://wiskundeolympiade.nl/files/opgaven/finale/2011/uitwerkingen_en.pdf",
        original_solution=[
            [0, 3, 1, 0, 0, 0],
            [0, 0, 1, 0, 3, 1],
            [1, 1, 0, 3, 0, 1],
            [3, 3, 0, 0, 1, 0],
            [3, 0, 3, 1, 0, 1],
            [3, 1, 1, 3, 1, 0]
        ],
        tags=[Tag.IS_ORIGINAL, Tag.COMBINATORICS, Tag.FIND_ANY]
    )
    n: int

    def __init__(self, n: int):
        self.n = n

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(n=self.n)

    def check(self, a: list[list[int]]) -> bool:
        # check validity matrix
        checker_format = self.check_format(a, is_integer=True, expected_length=self.n, is_square_matrix=True, min_val_inclusive=0, max_val_inclusive=3)
        if not checker_format[0]:
            return checker_format
        for i in (range(self.n)):
            for j in range(i):
                if a[j][i] == 1 and a[i][j] != 1:
                    return False, f"Invalid Matrix at {(i,j)} or {(j, i)}: The game between team {i} and team {j} should be a draw.", CheckerTag.INCORRECT_SOLUTION
                if a[j][i] == 3 and a[i][j] != 0:
                    return False, f"Invalid Matrix at {(i,j)} or {(j, i)}: Team {i} won against team {j}.", CheckerTag.INCORRECT_SOLUTION
                if a[j][i] == 0 and a[i][j] != 3:
                    return False, f"Invalid Matrix at {(i,j)} or {(j, i)}: Team {i} lost against team {j}.", CheckerTag.INCORRECT_SOLUTION
            if a[i][i] != 0:
                return False, f"Invalid Matrix at {(i,i)}: The diagonal should be 0.", CheckerTag.INCORRECT_SOLUTION
        sum_scores = [sum(row) for row in a]
        min_score = min(sum_scores)
        for score in range(min_score, min_score + self.n):
            if score not in sum_scores:
                return False, f"The scores should contain the numbers {min_score + 1} to {min_score + self.n}.", CheckerTag.INCORRECT_SOLUTION
        return True, "OK"
    
    @classmethod
    def has_variations(cls):
        return False

    @staticmethod
    def generate() -> "ProblemDutch20113":
        n = 6
        return ProblemDutch20113(n)
    
    def get_solution(self):
        return self.config.original_solution
