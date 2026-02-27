from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["jbmo_shortlist/problem_2019_c4.py"]

import random
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
import numpy as np


EXTRA_FORMATTING_INSTRUCTIONS = r"""Output the board where cells are denoted with "w" or "b", namely "b" if the cell is colored black and $w$ if it is white. Output the answer between \verb|\begin{array}{...}| and \verb|\end{array}| inside of $\boxed{...}$. For example, $\boxed{\begin{array}{ccc}w & b & b \\ b & b & w \\ w & w & w\end{array}}$."""

def get_solution(N:int) -> list[list[str]]:
    grid = np.zeros((5, N))
    grid[0] = 1
    grid[:, 0] = 1
    grid[-1] = 1
    grid[:, -1] = 1
    grid[2, 2:-2] = 1
    grid = np.where(grid==1, 'b', 'w')
    return grid.tolist()

class ProblemJBMO2019C4(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=EXTRA_FORMATTING_INSTRUCTIONS,
        parameters=["N"],
        source="2019 JBMO Shortlist C4",
        original_parameters={"N": 50},
        original_solution=get_solution(50),
        problem_url="https://artofproblemsolving.com/community/c6h2268005p17622004",
        solution_url="https://artofproblemsolving.com/community/c6h2268005p17622004",
        tags=[Tag.COMBINATORICS, Tag.IS_GENERALIZED, Tag.FIND_MAX_MIN]
    )

    N: int

    def __init__(self, N):
        self.N = N


    def get_problem(self):
        return PROBLEM_TEMPLATE.format(N=self.N,n=3*self.N + 2)

    def check(self, x: list[list[str]]) -> bool:
        if len(x) != 5:
            return False, f"Example should contain 5 rows", CheckerTag.INCORRECT_LENGTH
        for row in x:
            if len(row) != self.N:
                return False, f"Each row should be of length {self.N}", CheckerTag.INCORRECT_FORMAT
        x = np.array(x)
        n_colored = np.sum(x == 'b')

        if n_colored != 3*self.N + 2:
            return False, "Number of colored squares is incorrect", CheckerTag.INCORRECT_FORMAT
        
        for i1 in range(5):
            for j1 in range(self.N):
                if x[i1][j1] not in ["b", "w"]:
                    return False, f"Entries should include only 'b' or 'w' (black or white cells respectively).", CheckerTag.INCORRECT_FORMAT

        for i1 in range(5):
            for j1 in range(self.N):
                if x[i1][j1] not in ["b", "w"]:
                    return False, f"Entries should include only 'b' or 'w' (black or white cells respectively).", CheckerTag.INCORRECT_FORMAT
                n_neighbors = 0
                for i2 in range(max(i1-1,0), min(i1+2, 5)):
                    if i1 == i2:
                        continue
                    if x[i2][j1] == 'b':
                        n_neighbors += 1
                for j2 in range(max(j1-1,0), min(j1+2, self.N)):
                    if j1==j2:
                        continue
                    if x[i1][j2] == 'b':
                        n_neighbors += 1
                if n_neighbors > 2:
                    return False, f"Cell at {i1}, {j1} contains >2 black neighbors", CheckerTag.INCORRECT_SOLUTION
        
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "ProblemJBMO2019C4":
        N = random.randint(20, 60)
        return ProblemJBMO2019C4(N)

    def get_solution(self):
        return get_solution(self.N)
