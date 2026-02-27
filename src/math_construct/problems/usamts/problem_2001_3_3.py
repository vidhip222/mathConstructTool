from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["usamts/problem_2001_3_3.py"]

import random
from sympy import Poly, symbols
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_list_template


def get_solution(n: int) -> list[int]:
    a = [0]*(n-4) + [4, 3, -1, 2]
    return a

class Problem9(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_list_template(),
        parameters=["n"],
        source="USAMTS 01/02 Round 3",
        original_parameters={"n": 21},
        original_solution=get_solution(21),
        problem_url="https://files.usamts.org/Problems_13_3.pdf",
        solution_url="https://files.usamts.org/Solutions_13_3.pdf",
        tags=[Tag.ALGEBRA, Tag.FIND_ANY]
    )
    n: int

    def __init__(self, n: int):
        self.n = n

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(n=self.n)

    def check(self, a: list[int]) -> bool:
        if len(a) != self.n:
            return False, f"List of size {len(a)}, should be {self.n}", CheckerTag.INCORRECT_LENGTH
        if not all(isinstance(y, int) for y in a):
            return False, "All elements should be integers", CheckerTag.INCORRECT_FORMAT
        x = symbols('x')
        p = Poly(reversed(a + [1]), x)
        q = p**2
        if not all(c >= 0 for c in q.all_coeffs()):
            return False, "Not all coefficients of (p(x))^2 are non-negative", CheckerTag.INCORRECT_SOLUTION
        if all(c >= 0 for c in p.all_coeffs()):
            return False, "All coefficients of p(x) are non-negative", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "Problem9":
        n = random.randint(21, 100)
        return Problem9(n)

    def get_solution(self) -> list[int]:
        return get_solution(self.n)
