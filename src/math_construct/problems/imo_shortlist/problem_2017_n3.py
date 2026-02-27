from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["imo_shortlist/problem_2017_n3.py"]

from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_list_template
import random


def get_solution(n: int) -> list[int]:
    a = 2
    while n%a != 0:
        a += 1
    return [a]*(n-1) + [0]

class Problem2017N3(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_list_template(),
        parameters=["n"],
        source="IMO 2017 Shortlist N3",
        original_parameters={"n": 30},
        original_solution=get_solution(30),
        problem_url="https://www.imo-official.org/problems/IMO2017SL.pdf#page=79",
        solution_url="https://www.imo-official.org/problems/IMO2017SL.pdf#page=79",
        tags=[Tag.NUMBER_THEORY, Tag.IS_SIMPLIFIED, Tag.FIND_ANY],
    )
    n: int

    def __init__(self, n: int):
        self.n = n 

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(n=self.n)
    
    def check(self, a: list[int]) -> tuple[bool, str]:
        if len(a) != self.n:
            return False, f"List of size {len(a)}, should be {self.n}", CheckerTag.INCORRECT_LENGTH
        if not all(isinstance(y, int) for y in a):
            return False, "All elements should be integers", CheckerTag.INCORRECT_FORMAT
        if sum(a) % self.n == 0:
            return False, f"Sum of {a} is divisible by {self.n}, not allowed", CheckerTag.INCORRECT_SOLUTION
        a = a + a
        for i in range(self.n):
            found = False
            for j in range(1, self.n):
                if sum(a[i:i+j]) % self.n == 0:
                    found = True
                    break
            if not found:
                return False, f"For i={i}, no partial sum is divisible by {self.n}", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "Problem2017N3":
        def is_prime(n: int) -> bool:
            if n < 2:
                return False
            for i in range(2, int(n**0.5) + 1):
                if n % i == 0:
                    return False
            return True
        ns = [n for n in range(20, 50) if not is_prime(n)]
        n = random.choice(ns)
        return Problem2017N3(n)

    def get_solution(self):
        return get_solution(self.n)
