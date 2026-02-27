from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["imo_shortlist/problem_2023_a5.py"]

import math
import random
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_list_template


def get_solution(n: int, k: int):
    res = []
    N = (n+1)//2
    m = math.ceil((N+1)/2)
    a, b = m, 2*N-m
    while a < b:
        res += [a, b]
        a += 1
        b -= 1
    assert a == b
    res += [a]
    a, b = n, 1
    while b < m:
        res += [a, b]
        a -= 1
        b += 1
    return res


class Problem2023A5(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_list_template(),
        parameters=["n", "k"],
        source="IMO Shortlist 2023 A5",
        original_parameters={"n": 59, "k": 16},
        original_solution=get_solution(59, 16),
        tags=[Tag.ALGEBRA, Tag.FIND_MAX_MIN, Tag.IS_SIMPLIFIED],
        problem_url="https://www.imo-official.org/problems/IMO2023SL.pdf#page=23",
        solution_url="https://www.imo-official.org/problems/IMO2023SL.pdf#page=23",
    )
    n: int
    k: int

    def __init__(self, n: int, k: int):
        self.n = n
        self.k = k

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(n=self.n, k=self.k)

    def check(self, a: list[int]) -> bool:
        if len(a) != self.n:
            return False, f"List of size {len(a)}, should be {self.n}", CheckerTag.INCORRECT_LENGTH
        if not all(isinstance(y, int) for y in a):
            return False, "All elements should be integers", CheckerTag.INCORRECT_FORMAT
        if set(a) != set(range(1, self.n+1)):
            return False, f"Set of {set(a)} is not equal to {set(range(1, self.n+1))}", CheckerTag.INCORRECT_FORMAT
        diffs = [abs(a[i+1] - a[i]) for i in range(self.n-1)]
        if set(diffs) != set(range(1, self.n)):
            return False, f"Set of {set(diffs)} is not equal to {set(range(1, self.n))}", CheckerTag.INCORRECT_SOLUTION
        if max(a[0], a[-1]) > self.k:
            return False, f"Max of {max(a[0], a[-1])} is less than {self.k}", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "Problem2023A5":
        N = 2*random.randint(10, 200)
        n = 2*N-1
        k = math.ceil((N+1)/2)
        return Problem2023A5(n, k)

    def get_solution(self):
        return get_solution(self.n, self.k)
