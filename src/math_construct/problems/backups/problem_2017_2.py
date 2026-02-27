from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["backups/problem_2017_2.py"]

import random
import numpy as np
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_matrix_template


def get_solution(n):
    all_ones = [[1 for _ in range(n)] for _ in range(n)]
    for i in range(n - 1):
        all_ones[i + 1][n - 1 - i] = 0
    return all_ones

class ProblemKonhauser20172(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_matrix_template(),
        parameters=["n"],
        source="Konhauser Problemfest 2017",
        original_parameters={"n": 5},
        problem_url="https://www.macalester.edu/mscs/wp-content/uploads/sites/591/2018/04/KP2017.pdf",
        solution_url="https://www.macalester.edu/mscs/wp-content/uploads/sites/591/2018/04/KP2017.pdf#page=3",
        original_solution=get_solution(5),
        tags=[Tag.IS_SIMPLIFIED, Tag.ALGEBRA, Tag.FIND_MAX_MIN] 
    )
    n: str

    def __init__(self, n: str):
        self.n = n

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(n=self.n)

    def check(self, sol: list[list[int]]) -> bool:
        checker_format = self.check_format(sol, expected_length=self.n, is_square_matrix=True)
        if not checker_format[0]:
            return checker_format
        count_elements = dict()
        for row in sol:
            for el in row:
                count_elements[el] = count_elements.get(el, 0) + 1
        max_count = max(count_elements.values())
        if max_count != self.n ** 2 - self.n + 1:
            return False, f"The maximum number of equal elements should be {self.n ** 2 - self.n + 1}, but is {max_count}.", CheckerTag.INCORRECT_SOLUTION

        determinant = np.linalg.det(sol)
        if -1e-8 <= determinant <= 1e-8:
            return False, "The determinant of the matrix should be nonzero.", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT
        
    @staticmethod
    def generate() -> "ProblemKonhauser20172":
        n = random.randint(4, 9)
        return ProblemKonhauser20172(n)
    
    def get_solution(self):
        return get_solution(self.n)
