from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["backups/problem_polish_mo_r2_p5.py"]

import random
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
import numpy as np
from sympy import primefactors


EXTRA_FORMATTING_INSTRUCTIONS = r"""Output the answer as a single number inside of $\boxed{...}$. For example, $\boxed{10}$."""

def get_solution(k:int) -> int:
    return 2**k-1

# def bitcount(n: int) -> int:
#     count = 0
#     while n > 0:
#         count = count + 1
#         n = n & (n-1)
#     return count

class ProblemPolish53_R2P5(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=EXTRA_FORMATTING_INSTRUCTIONS,
        parameters=["k"],
        source="53rd Polish Olympiad R2 P5",
        original_parameters={"k": 523},
        original_solution=get_solution(523),
        problem_url="https://om.sem.edu.pl/previous_olympiads/#53@Zadania",
        solution_url="https://om.sem.edu.pl/previous_olympiads/#53@Zadania",
        tags=[Tag.NUMBER_THEORY, Tag.IS_SIMPLIFIED, Tag.FIND_ANY]
    )

    k: int

    def __init__(self, k):
        self.k = k

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(k=self.k)

    def check(self, x: int) -> bool:
        # for i in range(x, x**2+1, x):
        #     if i.bit_count() != self.k:
        #         return False, f"Number {i} does not have {self.k} ones in its binary representation", CheckerTag.INCORRECT_SOLUTION
        if x != 2**self.k - 1:
            return False, f"Number {x} does not have {self.k} ones in its binary representation, or is suboptimal", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "ProblemPolish53_R2P5":
        k = random.randint(345, 1000)
        return ProblemPolish53_R2P5(k)

    def get_solution(self):
        return get_solution(self.k)
