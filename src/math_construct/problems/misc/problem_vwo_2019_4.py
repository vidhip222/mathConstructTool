from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["misc/problem_vwo_2019_4.py"]

import math
import random
import sympy
from fractions import Fraction
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_list_template


def get_solution(n: int) -> list[int]:
    if n % 2 == 1:
        if n % 4 == 1:
            k = n // 4
            return [1] + [i for i in range(n - 2, 0, -2)][:k] + [n] + [i for i in range(2, n, 2)][:k-1][::-1] + [n // 2] + [i for i in range(n - 1, 0, -2)][:k] + [i for i in range(3, n, 2)][:k - 1][::-1]
        k = n // 4
        return [1] + [i for i in range(n - 2, 0, -2)][:k] + [i for i in range(2, n, 2)][:k][::-1] + [n // 2 + 1] + [i for i in range(n - 1, 0, -2)][:k] + [n] + [i for i in range(3, n, 2)][:k][::-1]
    numbers = [1] + [i for i in range(n - 2, 0, -2)] + [n] + [i for i in range(n - 1, 2, -2)]
    return numbers

class ProblemVWO20194(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_list_template(),
        parameters=["n", "k"],
        source="Vlaamse Wiskunde Olympiade Finals 2019-2020",
        problem_url="https://www.vwo.be/vwo/wp-content/uploads/2020/09/onlinefinaleVWO.pdf",
        original_parameters={"n": 25, "k": 25},
        original_solution=get_solution(25),
        tags=[Tag.IS_SIMPLIFIED, Tag.IS_TRANSLATED, Tag.COMBINATORICS, Tag.FIND_ANY]
    )
    n: int
    k: int

    def __init__(self, n: int, k: int):
        self.n = n
        self.k = k

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(n=self.n, k=self.k)

    def check(self, a: list[int]) -> bool:
        checker_format = self.check_format(a, is_integer=True, expected_length=self.n, is_unique=True, min_val_inclusive=1, max_val_inclusive=self.n)
        if not checker_format[0]:
            return checker_format
        visited = [False] * self.n
        if 1 not in a:
            return False, "The walk should start in hoop 1.", CheckerTag.INCORRECT_SOLUTION
        index_1 = a.index(1)
        visited[index_1] = True
        current = index_1
        n_visited = 1
        for i in range(self.n - 1):
            current = (current + a[current]) % self.n
            if visited[current]:
                break
            visited[current] = True
            n_visited += 1
        if self.n % 2 == 0 and n_visited == self.n:
            return True, "OK", CheckerTag.CORRECT
        if self.n % 2 == 1 and n_visited == self.n - 1:
            return True, "OK", CheckerTag.CORRECT
        return False, f"The length of the walk should be {self.n} or {self.n - 1}, but is of length {n_visited}.", CheckerTag.INCORRECT_SOLUTION

    @staticmethod
    def generate() -> "ProblemVWO20194":
        n = random.randint(25, 60)
        k = n if n % 2 == 0 else n - 1
        return ProblemVWO20194(n, k)
    
    def get_solution(self):
        return get_solution(self.n)

