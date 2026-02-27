from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["backups/usamts_problem_1998_2_2.py"]

import math
import random
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_list_template


def get_solution(k: int) -> list[list[int]]:
    res = []
    for x in range(1, 100):
        if x % 2 == 0:
            continue
        for y in range(1, 100):
            if math.gcd(x, y) != 1:
                continue
            res += [[x*x, 2*y*y, x*y]]
            if len(res) >= k:
                break
    return res


class Problem6(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_list_template(extra_instructions="Each element of the list should be a triple of integers, e.g. (1, 2, 3)."),
        parameters=["k"],
        source="USAMTS 98/99 Round 2",
        original_parameters={"k": 70},
        original_solution=get_solution(70),
        problem_url="https://files.usamts.org/Problems_10_2.pdf",
        solution_url="https://files.usamts.org/Solutions_10_2.pdf",
        tags=[Tag.NUMBER_THEORY, Tag.IS_SIMPLIFIED, Tag.FIND_INF]
    )
    k: int

    def __init__(self, k: int):
        self.k = k

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(k=self.k)

    def check(self, x: list[list[int]]):
        def is_square(n: int) -> bool:
            return int(n**0.5)**2 == n
        if len(x) < self.k:
            return False, f"List of size {len(x)}, should be at least {self.k}", CheckerTag.INCORRECT_LENGTH
        for arr in x:
            if len(arr) != 3:
                return False, f"List of size {len(arr)}, should be 3", CheckerTag.INCORRECT_LENGTH
            a, b, c = arr[0], arr[1], arr[2]
            if math.gcd(a, b, c) != 1:
                return False, f"GCD of {a}, {b}, {c} is not 1", CheckerTag.INCORRECT_SOLUTION
            if not is_square(a**2 * b**2 + b**2 * c**2 + c**2 * a**2):
                return False, f"Expression {a**2 * b**2 + b**2 * c**2 + c**2 * a**2} is not a square", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "Problem6":
        k = random.randint(50, 100)
        return Problem6(k)

    def get_solution(self):
        return get_solution(self.k)
