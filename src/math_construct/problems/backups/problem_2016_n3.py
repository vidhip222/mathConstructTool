from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["backups/problem_2016_n3.py"]

# https://artofproblemsolving.com/community/c6h1885499p12843947

from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
import random


FORMATTING_INSTRUCTIONS = r"""Output the sequences as comma-separated tuples inside of \boxed, e.g. \boxed{(1, 2, 3), (10, 11, 12), (-9, 3, -4)}."""

def get_solution(k: int) -> list[list[int]]:
    res = [[1, -1, 0], [0, 1, -1], [-1, 1, 0], [0, -1, 1], [1, 0, -1], [-1, 0, 1]][:k]
    p = 2
    while len(res) < k:
        res += [[p, -p, 0], [0, p, -p], [-p, p, 0], [0, -p, p], [p, 0, -p], [-p, 0, p]]
        p += 1
    return res[:k]

class ProblemBMO2016N3(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=FORMATTING_INSTRUCTIONS,
        parameters=["k"],
        source="BMO 2016 Shortlist N3",
        original_parameters={"k": 10},
        original_solution=get_solution(10),
        problem_url="https://artofproblemsolving.com/community/c6h1885499p12843947",
        solution_url="https://artofproblemsolving.com/community/c6h1885499p12843947",
        tags=[Tag.ALGEBRA, Tag.FIND_INF, Tag.IS_SIMPLIFIED]
    )
    k: int

    def __init__(self, k: int):
        self.k = k

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(k=self.k)

    def check(self, x: list[tuple[int]]) -> bool:
        for i, entry in enumerate(x):
            x[i] = tuple(entry)
        if len(x) != self.k:
            return False, f"{self.k} examples expected, received {len(x)}", CheckerTag.INCORRECT_LENGTH
        if len(set(x)) != len(x):
            return False, f"Elements of {x} are non-distinct", CheckerTag.INCORRECT_FORMAT
        for seq in x:
            if (seq[0] + seq[1] + seq[2])**5 != 80*seq[0]*seq[1]*seq[2]*(seq[0]**2 + seq[1]**2 + seq[2]**2):
                return False, f" $(x + y + z)^5 = 80xyz(x^2 + y^2 + z^2)$ is not satisfied for $x={seq[0]}$, $y={seq[1]}$, $z={seq[2]}$.", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "ProblemBMO2016N3":
        k = random.randint(5, 25)
        return ProblemBMO2016N3(k)

    def get_solution(self):
        return get_solution(self.k)
