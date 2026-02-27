from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["backups/problem_2006_2_p3.py"]

# https://imomath.com/srb/zadaci/bilten2006.pdf
import random
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
import numpy as np


EXTRA_FORMATTING_INSTRUCTIONS = r"""Output the points as a list of coordinate pairs inside of $\boxed{...}$. For example, $\boxed{[(1,2), (0,0), (3,4)]}$."""

def get_solution(n:int) -> list[tuple[float]]:
    return [(2*i,0) for i in range(1, n+1)]

class ProblemSMO2006_2_3AP4(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=EXTRA_FORMATTING_INSTRUCTIONS,
        parameters=["n"],
        source="Serbian MO 2006 R2 3 razred A kategorija P4 (simplified)",
        original_parameters={"n": 30},
        original_solution=get_solution(30),
        problem_url="https://imomath.com/srb/zadaci/bilten2006.pdf",
        solution_url="https://imomath.com/srb/zadaci/bilten2006.pdf",
        tags=[Tag.GEOMETRY, Tag.IS_SIMPLIFIED, Tag.IS_TRANSLATED, Tag.FIND_ANY]
    )

    n: int

    def __init__(self, n):
        self.n = n

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(n=self.n, k=2*self.n-3)

    def check(self, x: list[list[str]]) -> bool:
        if len(x) != self.n:
            return False, f"Example should contain {self.n} entries", CheckerTag.INCORRECT_LENGTH
        
        for entry in x:
            if len(entry) != 2:
                return False, f"Each entry should be a pair of coordinates", CheckerTag.INCORRECT_FORMAT
            
        if len(set(entry)) != len(entry):
            return False, f"Example points should be distinct", CheckerTag.INCORRECT_FORMAT
        
        coords = set()

        for i in range(self.n):
            for j in range(i+1, self.n):
                new_mid = ((round(x[i][0] + x[j][0])/2, 8), round((x[i][1] + x[j][1])/2, 8))
                coords.add(new_mid)

        if len(coords) != 2*self.n-3:
            return False, f"Too many (or too few somehow) non-distinct midpoints", CheckerTag.INCORRECT_SOLUTION
        
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "ProblemSMO2006_2_3AP4":
        N = random.randint(10, 100)
        return ProblemSMO2006_2_3AP4(N)

    def get_solution(self):
        return get_solution(self.n)
