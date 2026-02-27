from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["swiss/problem_2024_5_selection.py"]

import math
import random
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag

LIST_FORMATTING_TEMPLATE = r"""Output the answer as a comma separated list of lists inside of $\boxed{...}$. The first list should from the sequence $a_1, ..., a_n$ and the second sequence forms $b_1, ..., b_n$."""


def get_solution(n):
    return [
        [k for k in range(1, n + 1)],
        [k + 1 for k in range(1, n + 1)]
    ]


class ProblemSwissSelection20245(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=LIST_FORMATTING_TEMPLATE,
        parameters=["n"],
        source="Swiss Math Olympiad IMO Selection 2024",
        problem_url="https://mathematical.olympiad.ch/fileadmin/user_upload/Archiv/Intranet/Olympiads/Mathematics/deploy/exams/2024/Selection/MasterSolution/selectionSolution2024.pdf#page=13",
        solution_url="https://mathematical.olympiad.ch/fileadmin/user_upload/Archiv/Intranet/Olympiads/Mathematics/deploy/exams/2024/Selection/MasterSolution/selectionSolution2024.pdf#page=13",
        original_parameters={"n": 10},
        original_solution=get_solution(10),
        tags=[Tag.IS_SIMPLIFIED, Tag.ALGEBRA, Tag.FIND_ANY] 
    )
    n: int

    def __init__(self, n: int):
        self.n = n

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(n=self.n)
        
    def check(self, a: list[list[int]]) -> bool:
        checker_format = self.check_format(a, is_integer=True, is_matrix=True,
                                           min_val_exclusive=0, expected_size_all_axes=[2, self.n])
        if not checker_format[0]:
            return checker_format
        products = []
        for i in range(self.n + 1):
            products.append(math.prod(a[1][:i] + a[0][i:]))
        if not all(products[i] - products[i - 1] == math.factorial(self.n) for i in range(1, len(products))):
            return False, "The products do not form an arithmetic progression with common difference n!.", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "ProblemSwissSelection20245":
        n = random.randint(10, 25)
        return ProblemSwissSelection20245(n)
    
    def get_solution(self):
        return get_solution(self.n)
