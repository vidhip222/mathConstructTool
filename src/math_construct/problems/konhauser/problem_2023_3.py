from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["konhauser/problem_2023_3.py"]

import math
import random
import sympy
from fractions import Fraction
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_list_template
import itertools


def get_solution(n: int, k: int):
    solutions = []
    pascales_triangle = [1]
    for i in range(n + 1):
        elements_below_n = [el <= n for el in pascales_triangle]
        indices = [i for i, x in enumerate(elements_below_n) if x]
        # loop over all possible combinations of indices, of each length
        for j in range(1, len(indices) + 1):
            for comb in itertools.combinations(indices, j):
                if sum([pascales_triangle[c] for c in comb]) == n:
                    new_row = [0] * len(pascales_triangle)
                    for c in comb:
                        new_row[c] = 1
                    solutions.append(new_row)
        new_pascales_triangle = [1] + [pascales_triangle[i] + pascales_triangle[i + 1] for i in range(len(pascales_triangle) - 1)] + [1]
        pascales_triangle = new_pascales_triangle
    return solutions[:k]

class ProblemKonhauser20233(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=r"Output the bottom rows of these pyramids as a comma separated list of lists inside of \boxed{...}. For example, \boxed{(1,1,0),(0,1,0),(0,0,1,1)}",
        parameters=["n", "k"],
        source="Konhauser Problemfest 2023 P3",
        original_parameters={"k": 14, "n": 10},
        problem_url="https://drive.google.com/file/d/1K6Sf1EUpUkj64cowt5m-RNdnQMc_iNBd/view", #page 2,
        solution_url="https://drive.google.com/file/d/1K6Sf1EUpUkj64cowt5m-RNdnQMc_iNBd/view", # page 5
        original_solution=get_solution(10, 14),
        tags=[Tag.IS_ORIGINAL, Tag.COMBINATORICS, Tag.FIND_ALL, Tag.IS_GENERALIZED, Tag.IS_SIMPLIFIED]
    )
    n: int
    k: int

    def __init__(self, n: int, k: int):
        self.n = n
        self.k = k

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(n=self.n, k=self.k)

    def check_pyramid(self, a: list[int]) -> bool:
        current_sum = a[:]
        while len(current_sum) > 1:
            new_sum = []
            for i in range(len(current_sum) - 1):
                new_sum.append(current_sum[i] + current_sum[i + 1])
            current_sum = new_sum[:]
        return current_sum[0] == self.n

    def suf(self, i: int) -> str:
        # Absolute overkill
        return "st" if i == 1 else "nd" if i == 2 else "rd" if i == 3 else "th"

    def check(self, a: list[list[int]]) -> bool:
        a = list(set([tuple(sol) for sol in a]))
        checker_format = self.check_format(a, expected_length=self.k, is_integer=True, 
                                           min_val_inclusive=0, max_val_inclusive=1)
        if not checker_format[0]:
            return checker_format
        for i in range(self.k):
            if not self.check_pyramid(list(a[i])):
                return False, f"The sum of the top of the {i+1}{self.suf(i+1)} Lockridge Pyramid {a[i]} is not {self.n}.", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT
        
    @staticmethod
    def generate() -> "ProblemKonhauser20233":
        #n = random.randint(12, 15)
        #max_k_n_dependent = {10: 14, 11: 18, 12: 14, 13: 10, 14: 11, 15: 18}
        #k = random.randint(9, max_k_n_dependent[n])
        good_pairs = [
            (10, 13), (10, 14), (11, 18), (12, 13), (12, 14), (13, 10), (14, 11), (15, 16), (15, 17), (15, 18)
        ]
        n, k = random.choice(good_pairs)
        return ProblemKonhauser20233(n, k)
    
    def get_solution(self):
        return get_solution(self.n, self.k)
