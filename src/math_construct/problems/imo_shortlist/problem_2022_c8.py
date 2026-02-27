from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["imo_shortlist/problem_2022_c8.py"]

import random
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_matrix_template



MAT = [
    [0, 0, 0, 1, 0, 0],
    [0, 1, 0, 0, 0, 1],
    [0, 0, 1, 0, 1, 0],
    [0, 1, 0, 0, 0, 1],
    [0, 0, 1, 0, 1, 0],
    [0, 1, 0, 0, 0, 1],
]

def get_matrix(n: int):
    if n <= 6:
        mat = [row[:n] for row in MAT[:n]]
    else:
        mat = get_matrix(n-1)
        # fill last column periodically
        for i in range(n-1):
            val = mat[i][n-1-6]
            mat[i] += [val]
        # fill last row periodically
        mat.append([])
        for j in range(n):
            mat[n-1].append(mat[n-3][j])
    return mat

def get_solution(n: int):
    a = [[0]*n for _ in range(n)]
    free_vals = list(range(1, n**2+1))
    def fill(i, j):
        for di, dj in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            ni, nj = i+di, j+dj
            if 0 <= ni < n and 0 <= nj < n and a[ni][nj] == 0:
                # find smallest one in free_vals that it is greater than a[i][j]
                val = min(x for x in free_vals if x > a[i][j])
                a[ni][nj] = val
                free_vals.remove(val)
                fill(ni, nj)
    mat = get_matrix(n)
    if n % 6 == 3:
        for i in range(4, n, 4):
            mat[i][n-1] = 0
    if n % 6 == 0:
        for i in range(3, n, 4):
            mat[i][n-1] = 0
    for i in range(n):
        for j in range(n):
            if mat[i][j] == 1:
                a[i][j] = free_vals[-1]
                free_vals.remove(a[i][j])
    for i in range(n):
        for j in range(n):
            if a[i][j] == 0:
                a[i][j] = free_vals[0]
                free_vals.pop(0)
                fill(i, j)
    return a


class Problem2022C8(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_matrix_template(),
        parameters=["n"],
        problem_url="https://artofproblemsolving.com/community/c6h2883218p25635163",
        solution_url="https://artofproblemsolving.com/community/c6h2883218p25635163",
        source="IMO Shortlist 2022 C8",
        original_parameters={"n": 19},
        original_solution=get_solution(19),
        tags=[Tag.COMBINATORICS, Tag.IS_SIMPLIFIED, Tag.FIND_MAX_MIN],
    )
    n: int

    def __init__(self, n: int):
        self.n = n

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(n=self.n, k=2*self.n*(self.n-1)+1)

    def check(self, a: list[list[int]]) -> bool:
        if len(a) != self.n:
            return False, f"List of size {len(a)}, should be {self.n}", CheckerTag.INCORRECT_LENGTH
        if not all(len(row) == self.n for row in a):
            return False, f"All rows should have length {self.n}", CheckerTag.INCORRECT_LENGTH
        all_nums = set([x for row in a for x in row])
        if all_nums != set(range(1, self.n**2+1)):
            return False, f"All numbers should be distinct numbers between 1 and n^2", CheckerTag.INCORRECT_FORMAT
        
        loc = {}
        for i in range(self.n):
            for j in range(self.n):
                loc[a[i][j]] = (i, j)
        
        tot = {}
        for val in range(1, self.n**2+1):
            i, j = loc[val]
            tot[(i, j)] = 0
            found = False
            for di, dj in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                ni, nj = i+di, j+dj
                if 0 <= ni < self.n and 0 <= nj < self.n and a[ni][nj] < val:
                    found = True
                    tot[(i, j)] += tot[(ni, nj)]
            if not found:
                tot[(i, j)] = 1
                
        if sum(tot.values()) != 2*self.n*(self.n-1)+1:
            return False, f"Total number of uphill paths is {sum(tot.values())}, should be {2*self.n*(self.n-1)+1}", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "Problem2022C8":
        n = random.randint(10, 25)
        return Problem2022C8(n)

    def get_solution(self):
        return get_solution(self.n)
