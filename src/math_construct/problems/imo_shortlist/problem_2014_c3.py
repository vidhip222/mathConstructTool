from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["imo_shortlist/problem_2014_c3.py"]

from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
import itertools
import math
import random
from fractions import Fraction
import numpy as np

FORMATTING_INSTRUCTIONS = r"""Output a comma-separated list of 1-based rook indices (so (1, 1) is the top left corner of the board) inside of \boxed, for example \boxed{((1,1), (4,5), (1,6))}."""

def get_solution(n: int, k: int) -> list[list[int]]:
    m = k*k 
    rooks = [] 
    for i in range(k):
        for j in range(k):
            rooks.append([i*k+j+1, j*k+i+1])
    
    # Slice down 
    while m > n:
        valid_rooks = [] 
        invalid_rooks = [] 
        for rook in rooks:
            i, j = rook
            if i <= m-1 and j <= m-1:
                valid_rooks.append(rook)
            else:
                invalid_rooks.append(rook)
        # can only be 1 or 2 invalid, if 1 we don't care, if 2 we fix
        if len(invalid_rooks) == 2:
            i1, j1 = invalid_rooks[0]
            i2, j2 = invalid_rooks[1]
            valid_rooks.append([min(i1, i2), min(j1, j2)])
        rooks = valid_rooks
        m -= 1
    return rooks


class Problem2014C3(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=FORMATTING_INSTRUCTIONS,
        parameters=["n", "k"],
        source="IMO 2014 Shortlist C3",
        original_parameters={"n": 22, "k": 5},
        original_solution=get_solution(22, 5),
        problem_url="https://www.imo-official.org/problems/IMO2014SL.pdf#page=31",
        solution_url="https://www.imo-official.org/problems/IMO2014SL.pdf#page=31",
        tags=[Tag.COMBINATORICS, Tag.FIND_MAX_MIN, Tag.IS_SIMPLIFIED]
    )
    n: int
    k: int

    def __init__(self, n: int, k: int):
        self.n = n 
        self.k = k

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(n=self.n, k=self.k)
    
    def check(self, solution: list[list[int]]) -> tuple[bool, str, CheckerTag]:
        n, k = self.n, self.k
        if len(solution) != n:
            return False, f"List of size {len(solution)}, should be {n} (as we are placing {n} rooks)", CheckerTag.INCORRECT_LENGTH
        for rook in solution:
            if len(rook) != 2:
                return False, f"List element {rook} is not a pair", CheckerTag.INCORRECT_FORMAT
            i, j = rook
            if not (1 <= i <= n and 1 <= j <= n):
                return False, f"Rook at ({i}, {j}) is out of bounds", CheckerTag.INCORRECT_FORMAT
        
        # Actual validity 
        rowc = [0 for _ in range(n+1)]
        colc = [0 for _ in range(n+1)]
        for i, j in solution:
            rowc[i] += 1
            colc[j] += 1
        for i in range(1, n+1):
            if rowc[i] != 1:
                return False, f"Row {i} does not have exactly one rook", CheckerTag.INCORRECT_SOLUTION
            if colc[i] != 1:
                return False, f"Column {i} does not have exactly one rook", CheckerTag.INCORRECT_SOLUTION
        rookset = set([str(rook) for rook in solution])
        for i in range(1, n-k+2):
            for j in range(1, n-k+2):
                # kxk square that starts here 
                has_rook = False
                for offi in range(k):
                    for offj in range(k):
                        if str([i+offi, j+offj]) in rookset:
                            has_rook = True
                            break
                    if has_rook:
                        break
                if not has_rook:
                    return False, f"No rook in square starting at ({i}, {j})", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @classmethod
    def generate_multiple_explicit(cls, n_problems: int = None) -> list["Problem"]:
        ks = list(range(2, 25, 2))
        ret = [] 
        for k in ks:
            ret.append(cls(k*k-1, k)) # most of these were there before
            ret.append(cls(k*k, k)) # new 12
        return ret 

    @staticmethod
    def generate() -> "Problem2014C3":
        k = random.randint(4, 6)
        if k == 4: 
            n = 16 - random.randint(0, 1) # min: 15
        elif k == 5: 
            n = 25 - random.randint(0, 8) # min: 17
        elif k == 6:
            n = 36 - random.randint(0, 10) # min: 26
        else:
            raise RuntimeError("Invalid k")
        return Problem2014C3(n, k)

    def get_solution(self):
        return get_solution(self.n, self.k)
