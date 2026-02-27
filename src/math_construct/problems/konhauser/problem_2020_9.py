from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["konhauser/problem_2020_9.py"]

import math
import random
import sympy
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_list_template


def get_solution(p1, p2, p3, p4):
    return [
        p1 ** 2 * p3 * p4,
        p1 ** 2,
        p1 ** 2 * p3,
        p2 * p3,
        p2 ** 3,
        p2,
        p1 * p4
    ]

class ProblemKonhauser20209(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_list_template(r"The first number should be the last least common multiple and the numbers after need to be $a,b,c,d,e,f$ in order."),
        parameters=["p1", "p2", "p3", "p4"],
        source="Konhauser Problemfest 2020 P9",
        problem_url="https://www.macalester.edu/mscs/wp-content/uploads/sites/591/2020/05/Konhauser2020problems.pdf#page=2",
        solution_url="https://www.macalester.edu/mscs/wp-content/uploads/sites/591/2020/05/Konhauser2020problems.pdf#page=7",
        original_parameters={"p1": 2, "p2": 3, "p3": 5, "p4": 101},
        original_solution=get_solution(2, 3, 5, 101),
        tags=[Tag.IS_SIMPLIFIED, Tag.ALGEBRA, Tag.FIND_ANY, Tag.IS_ORIGINAL, Tag.IS_GENERALIZED] 
    )
    p1: int
    p2: int
    p3: int
    p4: int

    def __init__(self, p1: int, p2: int, p3: int, p4: int):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.p4 = p4

    def get_lcms(self) -> list[int]:
        abc = self.p1 ** 2 * self.p2 * self.p3
        bcd = self.p1 ** 2 * self.p2 ** 3 * self.p3
        cde = self.p2 ** 3 * self.p3
        def_ = self.p1 * self.p2 ** 3 * self.p4
        efa = self.p1 ** 2 * self.p2 * self.p4
        return [abc, bcd, cde, def_, efa]

    def get_problem(self):
        abc, bcd, cde, def_, efa = self.get_lcms()
        return PROBLEM_TEMPLATE.format(abc=abc, bcd=bcd, cde=cde, def_=def_, efa=efa)

    def check(self, sol: list[int]) -> bool:
        checker_format = self.check_format(sol, expected_length=7, is_integer=True, min_val_exclusive=0)
        if not checker_format[0]:
            return checker_format
        if len(set(sol[1:])) != 6:
            return False, "All numbers should be distinct.", CheckerTag.INCORRECT_FORMAT
        lcms = self.get_lcms()
        x, a, b, c, d, e, f = sol
        if math.lcm(f, a, b) != x:
            return False, f"The last lcm should be {x}.", CheckerTag.INCORRECT_SOLUTION
        if math.lcm(a, b, c) != lcms[0]:
            return False, f"The lcm of {a}, {b}, {c} should be {lcms[0]}.", CheckerTag.INCORRECT_SOLUTION
        if math.lcm(b, c, d) != lcms[1]:
            return False, f"The lcm of {b}, {c}, {d} should be {lcms[1]}.", CheckerTag.INCORRECT_SOLUTION
        if math.lcm(c, d, e) != lcms[2]:
            return False, f"The lcm of {c}, {d}, {e} should be {lcms[2]}.", CheckerTag.INCORRECT_SOLUTION
        if math.lcm(d, e, f) != lcms[3]:
            return False, f"The lcm of {d}, {e}, {f} should be {lcms[3]}.", CheckerTag.INCORRECT_SOLUTION
        if math.lcm(e, f, a) != lcms[4]:
            return False, f"The lcm of {e}, {f}, {a} should be {lcms[4]}.", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

        
    @staticmethod
    def generate() -> "ProblemKonhauser20209":
        primes = list(sympy.primerange(2, 100))
        p1, p2, p3, p4 = 1, 1, 1, 1
        while p1 == p2 or p2 == p3 or p3 == p4 or p4 == p1 or p1 == p3 or p2 == p4:
            p1 = random.choice(primes)
            p2 = random.choice(primes)
            p3 = random.choice(primes)
            p4 = random.choice(primes)
        return ProblemKonhauser20209(p1, p2, p3, p4)
    
    def get_solution(self) -> list[int]:
        return get_solution(self.p1, self.p2, self.p3, self.p4)
