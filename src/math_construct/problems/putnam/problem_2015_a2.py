from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["putnam/problem_2015_a2.py"]

import math
import random
from fractions import Fraction
from sympy import primefactors, isprime
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_integer_template



def get_solution(n: int) -> list[int]:
    # lemma states a_{kn} is divisible by a_{n}
    a = [1, 2]
    for i in range(2, 25):
        a.append(4*a[-1]-a[-2])
        if i>2 and n%i == 0:
            ps = primefactors(a[-1])
            for p in ps:
                if p != 2:
                    return p
    return None
    

class Problem_Putnam2015A2(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_integer_template(),
        parameters=["n"],
        source="Putnam 2015 A2",
        original_parameters={"n": 2015},
        original_solution=get_solution(2015),
        tags=[Tag.NUMBER_THEORY, Tag.IS_ORIGINAL, Tag.FIND_ANY, Tag.IS_GENERALIZED],
        problem_url="https://kskedlaya.org/putnam-archive/2015.pdf",
        solution_url="https://kskedlaya.org/putnam-archive/2015s.pdf",
    )
    n: int

    def __init__(self, n: int):
        self.n = n

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(n=self.n)

    def check(self, p: int) -> tuple[bool, str]:
        if not isinstance(p, int):
            return False, "p should be an integer", CheckerTag.INCORRECT_FORMAT
        if p == 2 or not isprime(p):
            return False, "Not a prime number", CheckerTag.INCORRECT_SOLUTION
        a = [1, 2]
        for i in range(2, self.n+1):
            a.append((4*a[-1]-a[-2])%p)
        if a[self.n] != 0:
            return False, "a_n not divisible by p", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "Problem_Putnam2015A2":
        a = [1, 2]
        good = []
        for i in range(2, 25):
            a.append(4*a[-1]-a[-2])
            ps = primefactors(a[-1])
            if any(p%2 == 1 for p in ps) and i%2 == 1:
                good += [i]

        # Find random multiple from numbers in good
        n = random.choice(good)
        m = 2*random.randint(1, 500)+1
        return Problem_Putnam2015A2(n*m)

    def get_solution(self):
        return get_solution(self.n)
