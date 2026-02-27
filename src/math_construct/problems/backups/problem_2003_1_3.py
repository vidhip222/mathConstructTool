from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["backups/problem_2003_1_3.py"]

import random
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_list_template


def get_solution(n: int) -> list[int]:
    if n == 2:
        return [1, 2]
    a = get_solution(n-1)
    if a[0] == n-1:
        return a + [n]
    return [n] + a

class Problem2(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_list_template(),
        parameters=["n"],
        source="USAMTS 23/24 Round 1",
        original_parameters={"n": 7},
        original_solution=[7, 5, 3, 1, 2, 4, 6],
        problem_url="https://files.usamts.org/Problems_35_1.pdf",
        solution_url="https://files.usamts.org/Solutions_35_1.pdf",
        tag=[Tag.PUZZLE, Tag.IS_GENERALIZED, Tag.FIND_MAX_MIN]
    )
    n: int

    def __init__(self, n: int):
        self.n = n

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(n=self.n, k=2*self.n-3)

    def check(self, heights: list[int]) -> bool:
        if not all(isinstance(y, int) for y in heights):
            return False, "All elements should be integers", CheckerTag.INCORRECT_FORMAT
        cnt = 0
        for i in range(len(heights)):
            for j in range(i+1, len(heights)):
                if j == i + 1 or min(heights[i], heights[j]) > max(heights[i+1:j]):
                    cnt += 1
        if cnt != 2 * self.n - 3:
            return False, f"Number of roof-friendly pairs is {cnt}, should be {2 * self.n - 3}", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "Problem2":
        n = random.randint(20, 100)
        return Problem2(n)

    def get_solution(self):
        return get_solution(self.n)
