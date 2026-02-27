from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["imc/problem_2019_9.py"]

import random
import numpy as np
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_list_template


FORMATTING_INSTRUCTIONS = r"""Output the matrices inside of \boxed{...} in the following format:
\boxed{
    \begin{pmatrix}
        ...
    \end{pmatrix},
    \begin{pmatrix}
        ...
    \end{pmatrix}
}
where the first matrix is $A$ and the second matrix is $B$.
"""

def get_solution(n: int):
    A = [[0,1], [1,0]]
    B = [[-1,1], [-1,-1]]
    for i in range(n//2-1):
        A = [x + [0, 0] for x in A]
        A.append([0] * (len(A[-1])-2) + [0, 1])
        A.append([0] * (len(A[-1])-2) + [1, 0])
        B = [x + [0, 0] for x in B]
        B.append([0] * (len(B[-1])-2) + [-1, 1])
        B.append([0] * (len(B[-1])-2) + [-1, -1])
    return [A, B]


class Problem_IMC_2019_9(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=FORMATTING_INSTRUCTIONS,
        parameters=["n"],
        source="IMC 2019 P9",
        original_parameters={"n": 4},
        original_solution=get_solution(4),
        problem_url="https://www.imc-math.org.uk/imc2019/imc2019-day2-solutions.pdf#page=2",
        solution_url="https://www.imc-math.org.uk/imc2019/imc2019-day2-solutions.pdf#page=2",
        tags=[Tag.ALGEBRA, Tag.IS_SIMPLIFIED, Tag.FIND_ANY],
    )
    n: int

    def __init__(self, n: int):
        self.n = n

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(n=self.n)

    def check(self, x: list[list[list[float]]]) -> bool:
        A, B = x[0], x[1]
        A = np.array(A)
        B = np.array(B)
        # check dimensions
        if A.shape != (self.n, self.n) or B.shape != (self.n, self.n):
            return False, f"The dimensions of A and B are not {self.n}x{self.n}.", CheckerTag.INCORRECT_LENGTH
        # check invertibility
        if abs(np.linalg.det(A)) < 1e-5 or abs(np.linalg.det(B)) < 1e-5:
            return False, f"A or B is not invertible.", CheckerTag.INCORRECT_SOLUTION
        # check AB - BA = B^2 A
        if not np.allclose(A @ B - B @ A, B @ B @ A):
            return False, f"AB - BA is not equal to B^2 A.", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "Problem_IMC_2019_9":
        n = 2*random.randint(3,9)
        return Problem_IMC_2019_9(n)

    def get_solution(self):
        return get_solution(self.n)
