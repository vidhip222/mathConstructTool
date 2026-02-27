from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["backups/problem_2023_2.py"]

import random
from itertools import combinations
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_list_template


def get_solution(k: int) -> list[float]:
    res = {2: [-3,-2,-1,1,2,3], 3: [-3,-2,-1,0,1,2,3]}
    for l in range(2, k-1):
        t = res[l][-1] + res[l][-2]
        res[l+2] = sorted(res[l] + [t, -t])
    return [float(x) for x in res[k]]

def get_basic_solution(k: int) -> list[float]:
    n = k+4
    if n%2 == 0:
        return [i for i in range(1, n//2+1)] + [-i for i in range(1, n//2+1)]
    else:
        return [i for i in range(1, n//2+1)] + [-i for i in range(1, n//2+1)] + [0]

class Problem_HMO_2023_2(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_list_template(),
        parameters=["k"],
        source="HMO 2023 2",
        original_parameters={"k": 10},
        original_solution=get_solution(10),
        problem_url="https://natjecanja.math.hr/wp-content/uploads/2024/01/2023_HMO-5.pdf#page=6",
        solution_url="https://natjecanja.math.hr/wp-content/uploads/2024/01/2023_HMO-5.pdf#page=6",
        tags=[Tag.NUMBER_THEORY, Tag.FIND_MAX_MIN, Tag.IS_SIMPLIFIED],
    )
    k: int

    def __init__(self, k: int):
        self.k = k

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(k=self.k)

    def check(self, a: list[float]):
        if len(a) != self.k+4:
            return False, f"The length of sequence a is different from {self.k+4}", CheckerTag.INCORRECT_LENGTH

        for i, target in enumerate(a):
            without_a = a[:i] + a[i+1:]
            found = False
            for comb in combinations(without_a, self.k):
                if abs(sum(comb)-target) < 1e-3:
                    found = True
                    break
            if not found:
                return False, f"Could not write {target} as sum of {self.k} elements", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "Problem_HMO_2023_2":
        k = random.randint(6, 20)
        return Problem_HMO_2023_2(k)

