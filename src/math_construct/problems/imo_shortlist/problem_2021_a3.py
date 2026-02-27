from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["imo_shortlist/problem_2021_a3.py"]

import math
import random
from fractions import Fraction
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_list_template


def get_solution(n: int):
    res = []
    k = 0
    while 2**(k+1) <= n:
        res.append(2**(k+1)-1)
        for i in range(2**k, 2**(k+1)-1):
            res.append(i)
        k += 1
    res.append(n)
    for i in range(2**k, n):
        res.append(i)
    return res

class Problem2021A3(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_list_template(),
        parameters=["n"],
        source="IMO Shortlist 2021 A3",
        original_parameters={"n": 30},
        original_solution=get_solution(30),
        problem_url="https://www.imo-official.org/problems/IMO2021SL.pdf#page=16",
        solution_url="https://www.imo-official.org/problems/IMO2021SL.pdf#page=16",
        tags=[Tag.NUMBER_THEORY, Tag.IS_SIMPLIFIED, Tag.FIND_MAX_MIN],
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
        if set(a) != set(range(1, self.n+1)):
            return False, f"The list is not a permutation of {range(1, self.n+1)}", CheckerTag.INCORRECT_FORMAT
        target = 1 + math.floor(math.log2(self.n))
        s = sum(math.floor(a[i]/(i+1)) for i in range(self.n))
        if s != target:
            return False, f"The sum of the floor values is {s}, should be {target}", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "Problem2021A3":
        n = random.randint(25, 50)
        return Problem2021A3(n)

    def get_solution(self):
        return get_solution(self.n)
