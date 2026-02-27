from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["imo_shortlist/problem_2022_c1.py"]

import math
import random
import sympy
from fractions import Fraction
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_list_template


def get_solution(n: int, C: int):
    tmp = [1,-1, -1, 1]
    res = [tmp[i % 4] for i in range(n)]
    return res


class Problem2022C1(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_list_template(),
        parameters=["n", "C"],
        source="IMO Shortlist 2022 C1",
        original_parameters={"n": 62, "C": 16},
        original_solution=get_solution(62, 16),
        problem_url="https://www.imo-official.org/problems/IMO2022SL.pdf#page=26",
        solution_url="https://www.imo-official.org/problems/IMO2022SL.pdf#page=26",
        tags=[Tag.COMBINATORICS, Tag.IS_SIMPLIFIED, Tag.FIND_MAX_MIN],
    )
    n: int
    C: int

    def __init__(self, n: int, C: int):
        self.n = n
        self.C = C

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(n=self.n, C=self.C)

    def check(self, a: list[int]) -> bool:
        mem_max, mem_min = {}, {}
        def calc_max(i, curr_sum):
            if (i, curr_sum) in mem_max:
                return mem_max[(i, curr_sum)]
            ret = curr_sum
            for j in [i+1, i+2]:
                if j < len(a):
                    ret = max(ret, calc_max(j, curr_sum + a[j]))
            mem_max[(i, curr_sum)] = ret
            return ret
        def calc_min(i, curr_sum):
            if (i, curr_sum) in mem_min:
                return mem_min[(i, curr_sum)]
            ret = curr_sum
            for j in [i+1, i+2]:
                if j < len(a):
                    ret = min(ret, calc_min(j, curr_sum + a[j]))
            mem_min[(i, curr_sum)] = ret
            return ret

        if len(a) != self.n:
            return False, f"List of size {len(a)}, should be {self.n}", CheckerTag.INCORRECT_LENGTH
        if not all(x in [-1, 1] for x in a):
            return False, f"List contains elements not in the set {-1, 1}", CheckerTag.INCORRECT_FORMAT
        if not all(isinstance(y, int) for y in a):
            return False, "All elements should be integers", CheckerTag.INCORRECT_FORMAT
        min_sum, max_sum = [], []
        for i in range(len(a)):
            min_sum.append(calc_min(i, a[i]))
            max_sum.append(calc_max(i, a[i]))
        if min(min_sum) < -self.C or max(max_sum) > self.C:
            return False, f"Min sum is {min(min_sum)} and max sum is {max(max_sum)}, should be in the range [-{self.C}, {self.C}]", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "Problem2022C1":
        n = 4*random.randint(10, 25)+2
        C = (n+2)//4
        return Problem2022C1(n, C)

    def get_solution(self):
        return get_solution(self.n, self.C)
