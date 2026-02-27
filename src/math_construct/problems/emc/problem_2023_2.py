from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["emc/problem_2023_2.py"]


from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
import random
import math
from typing import List, Tuple
from scipy.spatial import ConvexHull


FORMATTING_INSTRUCTIONS = r"""Output the sequences as comma-separated tuples inside of \boxed, e.g. \boxed{(1, 2), (1, 2, 3), (1, 1)}. Tom removes the $i$-the point in the list on the $i$-th day"""

def get_solution(n: int) -> List[Tuple[float, float]]:
    angles = [math.pi * i / n for i in range(1, n)]
    Bi = [(math.cos(theta), math.sin(theta)) for theta in angles]
    x1, y1 = Bi[0]
    x2, y2 = Bi[-1]
    det = x1 * y2 - x2 * y1
    X = (1 * y2 - 1 * y1) / det
    Y = (x1 * 1 - x2 * 1) / det
    A = (X, Y)
    points = [A] + Bi
    
    return points

class ProblemEMC20232(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=FORMATTING_INSTRUCTIONS,
        parameters=["n"],
        source="EMC 2023 Juniors P2",
        original_parameters={"n": 10},
        original_solution=get_solution(10),
        problem_url="https://emc.mnm.hr/wp-content/uploads/2023/12/EMC_2023_Juniors_ENG_Solutions.pdf",
        solution_url="https://emc.mnm.hr/wp-content/uploads/2023/12/EMC_2023_Juniors_ENG_Solutions.pdf",
        tags=[Tag.IS_SIMPLIFIED, Tag.GEOMETRY, Tag.FIND_ANY] 
    )
    n: int

    def __init__(self, n: int):
        self.n = n

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(n=self.n)

    def check(self, x: list[list[int]]) -> bool:
        checker_format = self.check_format(x, is_matrix=True, expected_length=self.n)
        if not checker_format[0]:
            return checker_format

        # check that no three points are collinear
        for i in range(self.n):
            for j in range(i+1, self.n):
                for k in range(j+1, self.n):
                    if (x[j][0] - x[i][0]) * (x[k][1] - x[i][1]) == (x[j][1] - x[i][1]) * (x[k][0] - x[i][0]):
                        return False, f"Points {x[i]}, {x[j]}, {x[k]} are collinear", CheckerTag.INCORRECT_SOLUTION
        
        v_i = []
        for i in range(self.n-2):
            if i > 0:
                points = x[i:]
            else:
                points = x
            hull = ConvexHull(points)
            v_i.append(len(hull.vertices))
        vi_diff = [abs(v_i[i] - v_i[i+1]) for i in range(len(v_i)-1)]
        if sum(vi_diff) != 2*self.n-8:
            return False, f"Sum of differences is {sum(vi_diff)}, should be {2*self.n-8}", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "ProblemEMC20232":
        n = random.randint(5, 35)
        return ProblemEMC20232(n)

    def get_solution(self):
        return get_solution(self.n)
