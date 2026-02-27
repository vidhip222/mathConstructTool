from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["imo_shortlist/problem_2018_c1.py"]

import random
from itertools import combinations
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_list_template


def get_solution(n: int) -> list[int]:
    res = [1]
    for k in range(1, n):
        res.append(3**k)
        res.append(2*3**k)
    res.append((3**n+9)//2-1)
    return res


class Problem_IMOShortlist2018C1(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_list_template(),
        parameters=["n"],
        source="IMO Shortlist 2018 C1",
        original_parameters={"n": 10},
        original_solution=get_solution(10),
        problem_url="https://www.imo-official.org/problems/IMO2018SL.pdf#page=26",
        solution_url="https://www.imo-official.org/problems/IMO2018SL.pdf#page=26",
        tags=[Tag.COMBINATORICS, Tag.IS_SIMPLIFIED, Tag.FIND_ANY]
    )
    n: int

    def __init__(self, n: int):
        self.n = n

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(n=self.n)

    def check(self, x: list[int]) -> tuple[bool, str]:
        if len(x) != 2*self.n:
            return False, f"List of size {len(x)}, should be {2*self.n}", CheckerTag.INCORRECT_LENGTH
        if not all(isinstance(y, int) for y in x):
            return False, "All elements should be integers", CheckerTag.INCORRECT_FORMAT
        if len(set(x)) != len(x):
            return False, "List contains duplicates", CheckerTag.INCORRECT_SOLUTION
        if any(x[i] <= 0 for i in range(2*self.n)):
            return False, "List contains non-positive integers", CheckerTag.INCORRECT_FORMAT
        tot_sum = sum(x)
        for m in range(2, self.n+1):
            found = False
            for subset in combinations(x, m):
                subset_sum = sum(subset)
                if subset_sum * 2 == tot_sum:
                    found = True
                    break
            if not found:
                return False, f"No valid parititon for m={m}", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "Problem_IMOShortlist2018C1":
        n = random.randint(8, 12)
        return Problem_IMOShortlist2018C1(n)

    def get_solution(self):
        return get_solution(self.n)
