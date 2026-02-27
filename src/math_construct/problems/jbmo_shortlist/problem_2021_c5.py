from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["jbmo_shortlist/problem_2021_c5.py"]

import random
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
import numpy as np


EXTRA_FORMATTING_INSTRUCTIONS = r"""Output the board where cells are denoted with "o" or "r", namely "r" if the cell is colored red and "o" otherwise. Output the answer between \verb|\begin{array}{...}| and \verb|\end{array}| inside of $\boxed{...}$. For example, $\boxed{\begin{array}{ccc}o & r & r \\ r & r & o \\ o & o & o\end{array}}$."""

def get_solution(N:int, a:int, b:int) -> list[list[str]]:
    grid = [["r" if i < a and j < b else "o" for i in range(N)] for j in range(N)]
    return grid

class ProblemJBMO2021C5(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=EXTRA_FORMATTING_INSTRUCTIONS,
        parameters=["a", "b", "N"],
        source="2021 JBMO Shortlist C6",
        original_parameters={"N": 15, "a":11, "b":7},
        original_solution=get_solution(15, 11, 7),
        problem_url="https://artofproblemsolving.com/community/c6h2876425p25559146",
        solution_url="https://artofproblemsolving.com/community/c6h2876425p25559146",
        tags=[Tag.COMBINATORICS, Tag.IS_GENERALIZED, Tag.FIND_ANY]
    )
    a: int
    b: int
    N: int

    def __init__(self, N: int, a: int, b:int):
        self.N = N
        self.a = a
        self.b = b

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(N=self.N, a=self.a, b=self.b, n=self.a*self.b)

    def check(self, x: list[list[str]]) -> bool:
        if len(x) != self.N:
            return False, f"Example should contain {self.N} rows", CheckerTag.INCORRECT_LENGTH

        for row in x:
            if len(row) != self.N:
                return False, f"Each row should be of length {self.N}", CheckerTag.INCORRECT_FORMAT

        x = np.array(x)
        n_colored = np.sum(x == 'r')
        if n_colored != self.a*self.b:
            return False, "Number of colored squares is incorrect", CheckerTag.INCORRECT_FORMAT
        
        for i1 in range(self.N):
            for j1 in range(self.N):
                if x[i1][j1] not in ["r", "o"]:
                    return False, f"Entries should include only 'r' or 'o' (red or non-colored cells respectively).", CheckerTag.INCORRECT_FORMAT

        rows_to_traverse = set(range(self.N))
        cols_to_traverse = set(range(self.N))
        start = True
        while start or len(rows_to_remove) != 0 or len(cols_to_remove) != 0:
            start = False
            rows_to_remove = set()
            cols_to_remove = set()
            for i in rows_to_traverse:
                if np.sum(x[i] == 'r') >= self.a:
                    x[i] = 'r'
                    rows_to_remove.add(i)
            for i in cols_to_traverse:
                if np.sum(x[:, i] == 'r') >= self.b:
                    x[:,i] = 'r'
                    cols_to_remove.add(i)
            rows_to_traverse = rows_to_traverse - rows_to_remove
            cols_to_traverse = cols_to_traverse - cols_to_remove

        if np.sum(x == 'r') != self.N**2:
            return False, "Grid cannot be fully colored in this configuration", CheckerTag.INCORRECT_SOLUTION
        
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "ProblemJBMO2021C5":
        N = random.randint(4, 15)
        a = random.randint(2, N - 2)
        b = random.randint(2, N - 2)
        return ProblemJBMO2021C5(N, a, b)

    def get_solution(self):
        return get_solution(self.N, self.a, self.b)
