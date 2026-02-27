from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["backups/problem_2015_n2.py"]

# https://artofproblemsolving.com/community/c914508_2015_balkan_mo_shortlist
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import LIST_FORMATTING_TEMPLATE
import random
import numpy as np



def get_solution(k: int) -> list[list[int]]:
    fib = [1, 1]
    res = [1]
    while len(res) < k:
        fib.append(fib[-1] + fib[-2])
        if fib[-1] % len(fib) == 0:
            res.append(len(fib))
    return res

class ProblemBMO2015N2(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=LIST_FORMATTING_TEMPLATE,
        parameters=["N"],
        source="BMO 2015 Shortlist N2",
        original_parameters={"N": 20},
        original_solution=get_solution(20),
        problem_url="https://artofproblemsolving.com/community/c6h1889204p12883734",
        solution_url="https://artofproblemsolving.com/community/c6h1889204p12883734",
        tags=[Tag.NUMBER_THEORY, Tag.FIND_INF, Tag.IS_SIMPLIFIED]
    )
    N: int

    def __init__(self, N: int):
        self.N = N

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(N=self.N)

    def check(self, x: list[list[int]]) -> bool:
        if len(x) != self.N:
            return False, f"Expected {self.N} examples, received {len(x)}", CheckerTag.INCORRECT_LENGTH
        if len(set(x)) != len(x):
            return False, f"Elements of {x} are non-distinct", CheckerTag.INCORRECT_FORMAT
        vals = [[0, 1, 2, 6] for _ in range(len(x))]
        for i in range(4, max(x)+1):
            for j, proposal in enumerate(x):
                vals[j].append((2*vals[j][-1] + vals[j][-2] - 2*vals[j][-3] - vals[j][-4]) % proposal**2)
                if i == proposal and vals[j][-1] != 0:
                    return False, f"{proposal**2} does not divide {(2*vals[j][-1] + vals[j][-2] - 2*vals[j][-3] - vals[j][-4])}", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "ProblemBMO2015N2":
        k = random.randint(10, 100)
        return ProblemBMO2015N2(k)

    def get_solution(self):
        return get_solution(self.N)
