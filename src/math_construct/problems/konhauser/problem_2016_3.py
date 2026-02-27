from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["konhauser/problem_2016_3.py"]

import random
import numpy as np
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag

MATRIX_FORMATTING_TEMPLATE = r"""Output the answer as a list of two elements: one matrix between \verb|\begin{array}{...}| and \verb|\end{array}| and one list inside of $\boxed{...}$. A number indicates the color of the edge. The $i$-th element of the $j$-th row in the matrix indicates the color of the edge between $u_j$ and $v_i$. The $i$-th element of the list indicates the color of the edge between $v_i$ and $v_{(i+1) \text{mod}(\text{len}(v_i))}$.

For instance, the following is a valid solution for $C_{{5, 3}}$ with 7 colors:

$\boxed{
\begin{array}{ccc}
3 & 2 & 7 \\
2 & 6 & 4 \\
5 & 1 & 2 \\
4 & 3 & 1 \\
1 & 4 & 3 \\
\end{array},
(7, 5, 6)
}$

"""


def get_solution(n, m):
    matrix = np.array([[0 for _ in range(n)] for _ in range(m)])
    array = [0 for _ in range(n)]
    for i in range(n):
        matrix[:, i] = [(k + i) % m + 1 for k in range(m)]
    number_on_diag = int(matrix[0, -1])
    matrix[0, -1] = m + 1
    matrix[1, -2] = m + 2
    array = [m + 1 + i % 2 for i in range(n)]
    if n % 2 == 1:
        array[-1] = m + 2
    array[-2] = number_on_diag
    return [matrix.tolist(), array]

class ProblemKonhauser20163(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=MATRIX_FORMATTING_TEMPLATE,
        problem_url="https://www.macalester.edu/mscs/wp-content/uploads/sites/591/2016/03/Konhauser2016.pdf#page=2",
        solution_url="https://www.macalester.edu/mscs/wp-content/uploads/sites/591/2016/03/Konhauser2016.pdf#page=7",
        parameters=["n", "m"],
        source="Konhauser Problemfest 2016 P3",
        original_parameters={"n": 7, "m": 7},
        original_solution=get_solution(7, 7),
        tags=[Tag.IS_ORIGINAL, Tag.IS_GENERALIZED, Tag.FIND_ANY, Tag.COMBINATORICS]
    )
    n: int
    m: int

    def __init__(self, n: int, m: int):
        self.n = n
        self.m = m

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(n=self.n, m=self.m, colors=self.m + 2)

    def check(self, sol: list[list[list[int]]]) -> bool:
        checker_format = self.check_format(sol, expected_length=2, is_integer=True)
        if not checker_format[0]:
            return checker_format
        checker_format = self.check_format(sol[0], is_matrix=True, expected_length=self.m)
        if not checker_format[0]:
            return checker_format
        checker_format = self.check_format(sol[1], expected_length=self.n)
        if not checker_format[0]:
            return checker_format
        matrix, array = sol[0], sol[1]
        unique_colors = set(array)
        for row in matrix:
            unique_colors.update(set(row))
            if len(set(row)) != self.n:
                return False, f"Each row should have different colors, but {row} contains duplicate ones.", CheckerTag.INCORRECT_SOLUTION
        for i in range(len(matrix[0])):
            col = [matrix[j][i] for j in range(len(matrix))]
            col += [array[i], array[(i - 1) % len(array)]]
            if len(set(col)) != len(col):
                return False, f"Each column should have different colors, but {col} contains duplicate ones.", CheckerTag.INCORRECT_SOLUTION
        if len(unique_colors) > self.m + 2:
            return False, f"More than {self.m + 2} colors were used.", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT
        
    @staticmethod
    def generate() -> "ProblemKonhauser20163":
        n = 2 * random.randint(1, 4) + 1
        m = random.randint(n, 10)
        if m == 5 and n == 3:
            m += 1
        return ProblemKonhauser20163(n, m)
    
    def get_solution(self):
        return get_solution(self.n, self.m)
