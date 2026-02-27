from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["imo_shortlist/problem_2023_c2.py"]

import random
from sympy import multiplicity
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_list_template



def get_solution(k: int):
    L = 2**(k+1)-1
    return [2**(k-multiplicity(2, i)) for i in range(1, L+1)]


class Problem2023C2(Problem):
    """IMO Shortlist 2023 C2"""
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_list_template(),
        parameters=["k"],
        source="IMO Shortlist 2023 C2",
        original_parameters={"k": 5},
        original_solution=get_solution(5),
        tags=[Tag.COMBINATORICS, Tag.FIND_MAX_MIN, Tag.IS_SIMPLIFIED],
        problem_url="https://www.imo-official.org/problems/IMO2023SL.pdf#page=38",
        solution_url="https://www.imo-official.org/problems/IMO2023SL.pdf#page=38",
    )
    k: int

    def __init__(self, k: int):
        self.k = k
        self.L = 2**(k+1)-1

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(k=self.k, L=self.L)

    def check(self, a: list[int]) -> bool:
        mem = {}
        def check(i, j, curr_sum):
            if (i, j, curr_sum) in mem:
                return mem[(i, j, curr_sum)]
            if i == j:
                mem[(i, j, curr_sum)] = curr_sum + a[i] != 0 and curr_sum - a[i] != 0
                return mem[(i, j, curr_sum)]
            mem[(i, j, curr_sum)] = check(i+1, j, curr_sum+a[i]) and check(i+1, j, curr_sum-a[i])
            return mem[(i, j, curr_sum)]
        if len(a) != self.L:
            return False, f"List of size {len(a)}, should be {self.L}", CheckerTag.INCORRECT_LENGTH
        if not all(isinstance(y, int) for y in a):
            return False, "All elements should be integers", CheckerTag.INCORRECT_FORMAT
        if not all(1 <= x <= 2**self.k for x in a):
            return False, f"List contains elements not in the range [1, {2**self.k}]", CheckerTag.INCORRECT_FORMAT
        for j in range(self.L):
            mem.clear()
            for i in range(j+1):
                if not check(i, j, 0):
                    return False, f"Subsequence from {i} to {j} has sum 0", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "Problem2023C2":
        k = random.randint(3, 8)
        return Problem2023C2(k)

    def get_solution(self):
        return get_solution(self.k)
