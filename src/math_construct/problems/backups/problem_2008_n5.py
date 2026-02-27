from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["backups/problem_2008_n5.py"]

from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import LIST_FORMATTING_TEMPLATE
import numpy as np
import random



def get_solution(k:int, p:int) -> list[int]:
    res = []
    i = p//3+1
    while len(res) < k:
        res.append(4*p*(3*i - p))
        i+=1
    return res

class ProblemBMO2008N5(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=LIST_FORMATTING_TEMPLATE,
        parameters=["N", "p"],
        source="BMO 2008 Shortlist N5",
        original_parameters={"N":23, "p": 31},
        original_solution=get_solution(23, 31),
        problem_url="https://artofproblemsolving.com/community/c1120589_2008_balkan_mo_shortlist",
        solution_url="https://artofproblemsolving.com/community/c1120589_2008_balkan_mo_shortlist",
        tags=[Tag.NUMBER_THEORY, Tag.FIND_INF, Tag.IS_SIMPLIFIED]
    )
    N: int
    p: int

    def __init__(self, N: int, p:int):
        self.N = N
        self.p = p

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(N=self.N, p=self.p)

    def check(self, x: list[tuple[int]]) -> bool:
        if len(x) != self.N:
            return False, f'Expected {self.N} samples, received {len(x)}', CheckerTag.INCORRECT_LENGTH
        if len(x) != len(set(x)):
            return False, 'Examples are not distinct', CheckerTag.INCORRECT_FORMAT
        
        div = (2**(2*self.p) - 1)//3
        
        a_s = [0]
        for i in range(2,max(x)+1):
            if i%2==1:
                a_s.append((2*a_s[-1]) % div)
            else:
                a_s.append((a_s[-1] + 2) % div)
            if i in x and a_s[-1] % div != 0:
                return False, f"Example {div} does not divide {a_s[-1]}", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "ProblemBMO2008N5":
        m = random.randint(10, 60)
        ps = [23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293]
        p = ps[random.randint(0, len(ps) - 1)]
        return ProblemBMO2008N5(m, p)

    def get_solution(self):
        return get_solution(self.N, self.p)
