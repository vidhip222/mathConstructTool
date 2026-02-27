from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["jbmo_shortlist/problem_2023_c1.py"]

import random
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
import numpy as np


EXTRA_FORMATTING_INSTRUCTIONS = r"""Output the board where cells are denoted with "b" or "r", depending on the color. Output the answer between \verb|\begin{array}{...}| and \verb|\end{array}| inside of $\boxed{...}$. For example, $\boxed{\begin{array}{ccc}b & r & r \\ r & r & b \\ b & b & b\end{array}}$."""

def get_solution(M:int) -> list[list[str]]:
    N = 2*M-1
    grid = [['r' for _ in range(N)] for _ in range(N)]
    for i in range(M-1):
        grid[M-1][i] = 'b'
        grid[M-1][i+M] = 'b'
        for j in range(M): 
            grid[i][j+M-1] = 'b'
    return grid

def largest_monochromatic_square(grid, N):
    dp_red = [[0] * N for _ in range(N)]
    dp_blue = [[0] * N for _ in range(N)]
    max_size = 0

    for i in range(N):
        for j in range(N):
            if i == 0 or j == 0:
                dp_red[i][j] = 1 if grid[i][j] == 'r' else 0
                dp_blue[i][j] = 1 if grid[i][j] == 'b' else 0
            else:
                if grid[i][j] == 'r':
                    dp_red[i][j] = min(dp_red[i-1][j], dp_red[i][j-1], dp_red[i-1][j-1]) + 1
                if grid[i][j] == 'b':
                    dp_blue[i][j] = min(dp_blue[i-1][j], dp_blue[i][j-1], dp_blue[i-1][j-1]) + 1
            
            max_size = max(max_size, dp_red[i][j], dp_blue[i][j])
    
    return max_size

class ProblemJBMO2023C1(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=EXTRA_FORMATTING_INSTRUCTIONS,
        parameters=["N", "M"],
        source="2023 JBMO Shortlist C1",
        original_parameters={"N": 17, "M": 9},
        original_solution=get_solution(9),
        problem_url="https://artofproblemsolving.com/community/c6h3347813p31039678",
        solution_url="https://artofproblemsolving.com/community/c6h3347813p31039678",
        tags=[Tag.COMBINATORICS, Tag.FIND_ANY, Tag.IS_GENERALIZED]
    )
    M: int
    N: int

    def __init__(self, N: int, M: int):
        self.N = N
        self.M = M

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(N=self.N, M=self.M, n=self.N//2)

    def check(self, x: list[list[str]]) -> bool:
        if len(x) != self.N:
            return False, f"Example should contain {self.N} rows", CheckerTag.INCORRECT_LENGTH

        for row in x:
            if len(row) != self.N:
                return False, f"Each row should be of length {self.N}", CheckerTag.INCORRECT_FORMAT
        
        arr = np.array(x)
        n_blue_rows = ((arr=='b').sum(axis=1) > self.N/2).sum()
        n_red_cols = ((arr=='r').sum(axis=0) > self.N/2).sum()
        if n_blue_rows != self.N//2 + 1 or n_red_cols != self.N//2 + 1:
            return False, f"Number of blue-dominated rows or number of red-dominated columns is invalid.", CheckerTag.INCORRECT_SOLUTION
        
        for i1 in range(self.N):
            for j1 in range(self.N):
                if x[i1][j1] not in ["r", "b"]:
                    return False, f"Entries should include only 'r' or 'b' (red or blue cells respectively).", CheckerTag.INCORRECT_FORMAT

        if largest_monochromatic_square(x, self.N) != self.N//2:
            return False, f"Maximum monochromatic square is of size {largest_monochromatic_square(x, self.N)}, expected {self.N//2}", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "ProblemJBMO2023C1":
        M = random.randint(8, 11)
        return ProblemJBMO2023C1(2*M-1, M)

    def get_solution(self):
        return get_solution(self.M)
