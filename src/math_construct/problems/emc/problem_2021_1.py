from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["emc/problem_2021_1.py"]


from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_list_template
import random
import math
from typing import List


def get_solution(n: int) -> List:
    if n % 2 == 0:
        return [0.5 + i for i in range(n // 2)] + [i for i in range(n // 2, 0, -1)]
    else:
        return [0.5 + i for i in range((n - 1) // 2)] + [i for i in range((n - 1) // 2, -1, -1)]

class ProblemEMC20211(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_list_template(r"The $i$-th element of the list should be the label of the $i$-th vertex."),
        parameters=["n"],
        source="EMC 2021 Seniors P1",
        original_parameters={"n": 20},
        original_solution=get_solution(20),
        problem_url="https://emc.mnm.hr/wp-content/uploads/2021/12/EMC_2021_Seniors_ENG_Solutions-1.pdf",
        solution_url="https://emc.mnm.hr/wp-content/uploads/2021/12/EMC_2021_Seniors_ENG_Solutions-1.pdf",
        tags=[Tag.IS_GENERALIZED, Tag.GEOMETRY, Tag.FIND_ANY] 
    )
    n: int

    def __init__(self, n: int):
        self.n = n

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(n=self.n, d=self.n - 3)

    def check(self, x: list[list[float]]) -> bool:
        checker_format = self.check_format(x, expected_length=self.n)
        if not checker_format[0]:
            return checker_format
        
        for i in range(self.n):
            if abs(x[(i + 1) % self.n] - x[i]) > 1:
                return False, f"Labels of consecutive vertices differ by more than 1 at index {i}", CheckerTag.INCORRECT_SOLUTION
        
        n_diagonals = 0
        for i in range(self.n):
            for j in range(i):
                abs_diff_mod_n = min(abs(i - j), abs(j + self.n - i))
                if abs_diff_mod_n > 1 and abs(x[i] - x[j]) <= 1:
                    n_diagonals += 1
        if n_diagonals != self.n - 3:
            return False, f"Number of diagonals is {n_diagonals}, should be {self.n - 3}", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "ProblemEMC20211":
        n = random.randint(10, 50)
        return ProblemEMC20211(n)

    def get_solution(self):
        return get_solution(self.n)
