from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["croatian/problem_2023_5.py"]

import random
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.utils import get_latex_array


FORMATTING_INSTRUCTIONS = r"""Output the rectangles by replacing x with an integer, where cells corresponding to the same integer denote the same rectangle.

$${init_grid}$$

For example, the following grid consists of 4 rectangles denoted by the integers 0-3:
$$
\begin{{array}}{{ccc}}
0 & 0 & 2 \\
0 & 0 & 2 \\
1 & 3 & 3 \\
\end{{array}}
$$

Put the answer inside of $\boxed{{...}}$.
"""

def get_solution(k: int, l: int, n: int):
    assert n >= 2*(k-1) and n >= 2*(l-1)
    cnt = 0
    a = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if j >= 2*(k-1):
                a[i][j] = a[i][j-1]
                continue
            if i >= 2*(l-1):
                a[i][j] = a[i-1][j]
                continue
            if i<l-1 and j<k-1:
                a[i][j] = (cnt := cnt+1) if i == 0 else a[i-1][j]
            elif i<l-1:
                a[i][j] = (cnt := cnt+1) if j==k-1 else a[i][j-1]
            elif j<k-1:
                a[i][j] = (cnt := cnt+1) if j==0 else a[i][j-1]
            else:
                a[i][j] = (cnt := cnt+1) if i==l-1 else a[i-1][j]
    return a

class Problem_HMO_2023_5(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=FORMATTING_INSTRUCTIONS,
        parameters=["k", "l", "n"],
        source="HMO 2023 5",
        original_parameters={"k": 4, "l": 5, "n": 10},
        original_solution=get_solution(4, 5, 10),
        problem_url="https://natjecanja.math.hr/wp-content/uploads/2024/01/2023_HMO-5.pdf#page=21",
        solution_url="https://natjecanja.math.hr/wp-content/uploads/2024/01/2023_HMO-5.pdf#page=21",
        tags=[Tag.COMBINATORICS, Tag.FIND_MAX_MIN, Tag.IS_SIMPLIFIED],
    )
    k: int
    l: int
    n: int

    def __init__(self, k: int, l: int, n: int):
        self.k = k
        self.l = l
        self.n = n
        self.init_grid = get_latex_array([["x"] * self.n] * self.n)

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(k=self.k, l=self.l, n=self.n,m=2*(self.k+self.l-2), init_grid=self.init_grid)

    def get_formatting_instructions(self):
        return FORMATTING_INSTRUCTIONS.format(init_grid=self.init_grid)

    def check(self, a: list[list[int]]):
        if len(a) != self.n:
            return False, f"List of size {len(a)}, should be {self.n}", CheckerTag.INCORRECT_LENGTH
        for row in a:
            if len(row) != self.n:
                return False, f"Row of size {len(row)}, should be {self.n}", CheckerTag.INCORRECT_LENGTH
        
        coords = {}
        for i, row in enumerate(a):
            for j, c in enumerate(row):
                coords[c] = coords.get(c, []) + [(i, j)]
        m=2*(self.k+self.l-2)
        if len(coords.keys()) != m:
            return False, f"Solution does not use {m} rectangles", CheckerTag.INCORRECT_SOLUTION
        
        # check if all cells from the same digit form a square
        for d in coords.keys():
            # find bottom left
            min_i = min(coords[d], key=lambda x: x[0])[0]
            min_j = min(coords[d], key=lambda x: x[1])[1]
            # find top right
            max_i = max(coords[d], key=lambda x: x[0])[0]
            max_j = max(coords[d], key=lambda x: x[1])[1]
            # check if all cells from the same digit form a square
            for i in range(min_i, max_i+1):
                for j in range(min_j, max_j+1):
                    if (i, j) not in coords[d]:
                        return False, f"Cells corresponding to the integer {d} do not form a rectangle", CheckerTag.INCORRECT_SOLUTION

        # check if a line going through one row intersects at least k rectangles
        for i in range(len(a)):
            if len(set(a[i])) < self.k:
                return False, f"Line going through row {i} intersects less than {self.k} rectangles", CheckerTag.INCORRECT_SOLUTION
        # check if a line going through one column intersects at least l rectangles
        for j in range(len(a[0])):
            if len(set(a[i][j] for i in range(len(a)))) < self.l:
                return False, f"Line going through column {j} intersects less than {self.l} rectangles", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "Problem_HMO_2023_5":
        k = random.randint(4, 7)
        l = random.randint(4, 7)
        n = random.randint(max(2*(k-1), 2*(l-1)), max(2*(k-1), 2*(l-1))+5)
        return Problem_HMO_2023_5(k, l, n)

    def get_solution(self):
        return get_solution(self.k, self.l, self.n)
