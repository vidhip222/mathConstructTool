from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["misc/problem_handout_nz1.py"]

import random
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
import numpy as np
from sympy import factorint


EXTRA_FORMATTING_INSTRUCTIONS = r"""Output the answer as a list of numbers inside of $\boxed{...}$, where you should only give the first number for each pair. For example, $\boxed{[3, 6, 11]}$."""

def get_solution(n:int) -> list[tuple[float]]:
    res = [(8,9)]
    for _ in range(1, n):
        res.append((4*res[-1][0]*(res[-1][0] + 1), 4*res[-1][0]*(res[-1][0] + 1) + 1))
    return [r[0] for r in res]

class ProblemNZNT(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=EXTRA_FORMATTING_INSTRUCTIONS,
        parameters=["n"],
        source="New Zealand Squad Assignment Number Theory P3 (simplified)",
        original_parameters={"n": 8},
        original_solution=get_solution(8),
        problem_url="https://www.studocu.com/en-us/document/california-institute-of-technology/topics-in-number-theory/2011-squad-nt-solns-nt-stuff/114245476",
        solution_url="https://www.studocu.com/en-us/document/california-institute-of-technology/topics-in-number-theory/2011-squad-nt-solns-nt-stuff/114245476",
        tags=[Tag.NUMBER_THEORY, Tag.IS_SIMPLIFIED, Tag.FIND_INF]
    )

    n: int

    def __init__(self, n):
        self.n = n

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(n=self.n)

    def check(self, x: list[int]) -> bool:
        if len(x) != self.n:
            return False, f"Example should contain {self.n} entries", CheckerTag.INCORRECT_LENGTH
        
        if len(set(x)) != len(x):
            return False, f"Examples should be unique", CheckerTag.INCORRECT_FORMAT

        for i, n in enumerate(x):
            factorization_n = factorint(n)
            for p in factorization_n:
                if factorization_n[p] < 2:
                    return False, f"Prime divisor {p} of {n} only divides {n} once", CheckerTag.INCORRECT_SOLUTION
            factorization_n = factorint(n+1)
            for p in factorization_n:
                if factorization_n[p] < 2:
                    return False, f"Prime divisor {p} of {n+1} only divides {n+1} once" , CheckerTag.INCORRECT_SOLUTION        
        
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "ProblemNZNT":
        N = random.randint(7, 8)
        return ProblemNZNT(N)

    def get_solution(self):
        return get_solution(self.n)
