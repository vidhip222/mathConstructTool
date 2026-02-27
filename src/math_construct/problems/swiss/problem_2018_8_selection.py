from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["swiss/problem_2018_8_selection.py"]

import random
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_list_template
import numpy as np

def get_solution(k: int) -> list[int]:
    return [2 ** l - 2 for l in range(2, k + 1)]

class ProblemSwissSelection20188(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_list_template(),
        parameters=["k"],
        problem_url="https://mathematical.olympiad.ch/fileadmin/user_upload/Archiv/Intranet/Olympiads/Mathematics/deploy/exams/2018/Selection/MasterSolution/selectionSolution2018.pdf#page=12",
        solution_url="https://mathematical.olympiad.ch/fileadmin/user_upload/Archiv/Intranet/Olympiads/Mathematics/deploy/exams/2018/Selection/MasterSolution/selectionSolution2018.pdf#page=12",
        source="Swiss Math Olympiad IMO Selection 2020",
        original_parameters={"k": 15},
        original_solution=get_solution(15),
        tags=[Tag.IS_SIMPLIFIED, Tag.FIND_ALL, Tag.COMBINATORICS] 
    )
    k: int

    def __init__(self, k: int):
        self.k = k

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(k=self.k, k_minus_1=self.k - 1)
    
    def binomial_mod_2(self, n, i):
        """
        Returns (n choose i) mod 2.
        Equivalent to checking if (n & i) == i.
        """
        return 1 if (n & i) == i else 0
        
    def check(self, a: list[int]) -> bool:
        checker = self.check_format(a, is_integer=True, expected_length=self.k - 1, is_unique=True,
                                    min_val_exclusive=1, max_val_exclusive=2 ** self.k)
        if not checker[0]:
            return checker
        
        # brute-force also works, but let's not do that
        # for n in a:
        #     for i in range(n + 1):
        #         for j in range(n + 1):
        #             if (i + j) % 2 != self.binomial_mod_2(n, i) + self.binomial_mod_2(n, j):
        #                 return False, f"Property does not hold for n = {n}, i = {i}, j = {j}."
        # find all a not in self.get_solution
        for n in a:
            if n not in self.get_solution():
                return False, f"{n} does not satisfy the equation.", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @classmethod
    def generate_multiple_explicit(cls, n_problems: int = None) -> list["Problem"]:
        small = [2,4,6,8,10]
        mid = np.linspace(11, 25, 10).astype(int).tolist()
        big = np.linspace(30, 180, 9).astype(int).tolist()
        return [cls(k) for k in small + mid + big]

    @staticmethod
    def generate() -> "ProblemSwissSelection20188":
        k = random.randint(10, 25)
        return ProblemSwissSelection20188(k)
    
    def get_solution(self):
        return get_solution(self.k)
    
