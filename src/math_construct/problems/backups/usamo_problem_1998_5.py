from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["backups/usamo_problem_1998_5.py"]

import math
import random

from math_construct.problems.problem import CheckerTag, Problem, ProblemConfig, Tag
from math_construct.templates import get_list_template



def get_solution(n: int) -> list[list[int]]:
    if n == 2:
        return [0, 1]
    # a = get_solution(n-1)
    # m = math.prod(a)
    # k = math.prod((m-x)**2 for x in a)-1
    # b = [x+k*m for x in a]
    # res = b + [m+k*m]
    # return res
    s = get_solution(n - 1)
    L = 1
    for a in s:
        for b in s:
            if a != b:
                L = math.lcm(L, (a - b) ** 2)
                if a > 0 and b > 0:
                    L = math.lcm(L, a * b)
    res = [L + x for x in s] + [0]
    return res


class USAMO_1998_5(Problem):
    """1998 USAMO Problem 5"""

    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_list_template(),
        parameters=["n"],
        source="1998 USAMO Problem 5",
        original_parameters={"n": 6},
        original_solution=get_solution(6),
        problem_url="https://artofproblemsolving.com/wiki/index.php/1998_USAMO_Problems/Problem_5",
        solution_url="https://artofproblemsolving.com/wiki/index.php/1998_USAMO_Problems/Problem_5",
        tags=[Tag.NUMBER_THEORY, Tag.FIND_ANY],
    )
    n: int

    def __init__(self, n: int):
        self.n = n

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(n=self.n)

    def check(self, x: list[int]) -> bool:
        if len(set(x)) != self.n or len(x) != self.n:
            return (
                False,
                f"List either has duplicate elements or is not of length {self.n}",
                CheckerTag.INCORRECT_FORMAT,
            )
        if not all(isinstance(y, int) for y in x):
            return False, "All elements should be integers", CheckerTag.INCORRECT_FORMAT
        for i in range(self.n):
            for j in range(i + 1, self.n):
                if x[i] * x[j] % (x[i] - x[j]) ** 2 != 0:
                    return (
                        False,
                        f"Product {x[i]*x[j]} is not divisible by {(x[i]-x[j])**2}",
                        CheckerTag.INCORRECT_SOLUTION,
                    )
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "USAMO_1998_5":
        n = random.randint(6, 7)
        return USAMO_1998_5(n)

    def get_solution(self):
        return get_solution(self.n)


# for n in range(6, 10):
#    print(n, len(str(USAMO_1998_5(n).get_solution())))
