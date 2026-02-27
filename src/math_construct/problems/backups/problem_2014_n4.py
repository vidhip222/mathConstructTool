from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["backups/problem_2014_n4.py"]

# https://artofproblemsolving.com/community/c6h588119p3481502

from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag

import random


FORMATTING_INSTRUCTIONS = r"""Output the sequences as a list of comma-separated tuples ($n, a, b, c, d$) inside of \boxed, e.g. \boxed{(1, 2, 3, 4, 5), (7, 10, 11, 12, 14), (2, 3, 4, 9, 9)}."""

def get_solution(k: int) -> list[list[int]]:
    
    return [(9*i**3 + 9*i**2 + 3*i + 1, 3*i+1, 1, 1, 1) for i in range(1, k+1)]

class ProblemBMO2014N4(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=FORMATTING_INSTRUCTIONS,
        parameters=["N"],
        source="BMO 2014 Shortlist N4",
        original_parameters={"N": 25},
        original_solution=get_solution(25),
        problem_url="https://artofproblemsolving.com/community/c6h588119p3481502",
        solution_url="https://artofproblemsolving.com/community/c6h588119p3481502",
        tags=[Tag.NUMBER_THEORY, Tag.FIND_INF, Tag.IS_SIMPLIFIED]
    )
    N: int

    def __init__(self, N: int):
        self.N = N

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(N=self.N)

    def check(self, x: list[tuple[int]]) -> bool:
        if len(x) != self.N:
            return False, f"{self.N} examples expected, received {len(x)}", CheckerTag.INCORRECT_LENGTH
        
        for i, entry in enumerate(x):
            if len(entry) != 5:
                return False, f"Each sequence should contain 5 examples, received {entry}", CheckerTag.INCORRECT_FORMAT
            if entry[0] != (entry[1]**3 + 2*entry[2]**3)//(entry[3]**3 + 2*entry[4]**3) or (entry[1]**3 + 2*entry[2]**3) % (entry[3]**3 + 2*entry[4]**3) != 0:
                return False, f"{entry} does not satisfy  n = \\frac {{a^3 + 2b^3}} {{c^3 + 2d^3}}.", CheckerTag.INCORRECT_SOLUTION

        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "ProblemBMO2014N4":
        k = random.randint(15, 60)
        return ProblemBMO2014N4(k)

    def get_solution(self):
        return get_solution(self.N)
