from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["bxmo/problem_2019_2.py"]

import math
import random
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_matrix_template
from sympy import divisors


def get_solution(n):
    zeros_matrix = [[0 for _ in range(n)] for _ in range(n)]
    for i in range(n):
        min_val = max(n // 2 - i, n // 2 - (n - 1 - i))
        max_val = min(min_val + (2 * i), min_val + (2 * (n - 1 - i)))
        for j in range(0, max_val - min_val + 1):
            if j % 2 == 0:
                zeros_matrix[i][min_val + j] = 2
            else:
                zeros_matrix[i][min_val + j] = 1
    return zeros_matrix

class ProblemBxMO20192(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_matrix_template("If a square contains a rook, write 2. If a square contains a pawn, write 1. Otherwise, write 0."),
        problem_url="http://bxmo.org/problems/bxmo-problems-2019-zz.pdf",
        solution_url="http://bxmo.org/problems/bxmo-problems-2019-zz.pdf",
        parameters=["k", "n"],
        source="BxMO 2019 P2",
        original_parameters={"n": 9}, # not the original size, to make it parseable, complexity is the same though
        original_solution=get_solution(9),
        tags=[Tag.IS_SIMPLIFIED, Tag.COMBINATORICS, Tag.FIND_MAX_MIN, Tag.IS_GENERALIZED] 
    )
    n: int
    k: int

    def __init__(self, n: int, k: int = None):
        self.n = n
        self.k = n // 2

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(n=self.n, k=self.k)
        
    def check(self, a: list[list[int]]) -> bool:
        # check validity matrix
        correct, message, tag = self.check_format(a, is_integer=True, expected_length=self.n, is_square_matrix=True, min_val_inclusive=0, max_val_inclusive=2)
        if not correct:
            return correct, message, tag
        rooks, pawns = 0, 0
        for row in a:
            for i in row:
                if i == 1:
                    pawns += 1
                if i == 2:
                    rooks += 1
        if rooks != self.n + self.k ** 2:
            return False, f"There should be {self.n + self.k ** 2} rooks.", CheckerTag.INCORRECT_SOLUTION
        if pawns != self.k ** 2:
            return False, f"There should be {self.k ** 2} pawns.", CheckerTag.INCORRECT_SOLUTION
        for i in range(len(a)):
            for j in range(len(a)):
                if a[i][j] == 2:
                    for k in range(i + 1, len(a)):
                        if a[k][j] == 2:
                            return False, f"Rooks at ({i}, {j}) and ({k}, {j}) can see each other.", CheckerTag.INCORRECT_SOLUTION
                        if a[k][j] == 1:
                            break
                    for k in range(j + 1, len(a)):
                        if a[i][k] == 2:
                            return False, f"Rooks at ({i}, {j}) and ({i}, {k}) can see each other.", CheckerTag.INCORRECT_SOLUTION
                        if a[i][k] == 1:
                            break
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "ProblemBxMO20192":
        n = 2 * random.randint(2, 10) + 1
        return ProblemBxMO20192(n)
    
    def get_solution(self):
        return get_solution(self.n)
