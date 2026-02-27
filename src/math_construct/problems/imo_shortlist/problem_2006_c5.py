from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["imo_shortlist/problem_2006_c5.py"]

from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
import itertools
import math
import random


FORMATTING_INSTRUCTIONS = r"""Output a comma-separated list of rounds, inside of \boxed. Each round is itself a list of numbers, where the i-th number indicates the player that player i meets in that round (1-indexed). For example, a well-formatted output for k=2 and n=4 is \boxed{(4, 3, 2, 1), (3, 4, 1, 2)}."""

def get_solution(n: int, k: int) -> list[list[int]]:
    m = 1 
    while n % (2*m) == 0:
        m *= 2

    ret = [] 
    for i in range(1, k+1): 
        # solve for (m, k) 
        core = [a ^ i for a in range(m)]

        # repeat to (n, k)
        full_round = []
        for shift in range(0, n, m):
            full_round += [a + shift for a in core]

        ret.append([a+1 for a in full_round]) # 1-indexing
    return ret 

class Problem2006C5(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=FORMATTING_INSTRUCTIONS,
        parameters=["n", "k"],
        source="IMO 2006 Shortlist C5",
        original_parameters={"n": 24, "k": 5},
        original_solution=get_solution(24, 5),
        problem_url="https://www.imo-official.org/problems/IMO2006SL.pdf#page=28",
        solution_url="https://www.imo-official.org/problems/IMO2006SL.pdf#page=28",
        tags=[Tag.COMBINATORICS, Tag.FIND_ALL, Tag.IS_SIMPLIFIED] 
    )
    n: int
    k: int

    def __init__(self, n: int, k: int):
        self.n = n
        self.k = k

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(n=self.n, k=self.k)
    
    def check(self, solution: list[list[int]]) -> tuple[bool, str, CheckerTag]:
        # format and move to 0 indexing
        if len(solution) != self.k:
            return False, f"List of size {len(solution)}, should be {self.k}", CheckerTag.INCORRECT_LENGTH
        if any(len(rnd) != self.n for rnd in solution):
            return False, f"Some round not of size {self.n}", CheckerTag.INCORRECT_FORMAT
        for rnd in solution:
            for player in rnd:
                if player < 1 or player > self.n:
                    return False, f"Player {player} out of bounds", CheckerTag.INCORRECT_FORMAT
        if any(len(set(rnd)) != self.n for rnd in solution):
            return False, f"Duplicate players in a round", CheckerTag.INCORRECT_FORMAT
        solution = [[player - 1 for player in rnd] for rnd in solution]

        # every two players meet at most once + fill the map for the cycle requirement 
        rnd_met = [[-1 for _ in range(self.n)] for _ in range(self.n)]
        for i in range(self.k):
            for a in range(self.n):
                b = solution[i][a]
                if a == b:
                    return False, f"Self pairing found in round {i+1} for player {a+1}", CheckerTag.INCORRECT_SOLUTION
                if solution[i][b] != a:
                    return False, f"Pairing not mutual: round {i+1}, players {a+1} and {b+1}", CheckerTag.INCORRECT_SOLUTION
                if rnd_met[a][b] != -1:
                    return False, f"Two players {a+1} and {b+1} met more than once", CheckerTag.INCORRECT_SOLUTION
                rnd_met[a][b] = i
        
        # cycle requirement 
        for i in range(self.k):
            for a in range(self.n): 
                for c in range(self.n):
                    if a == c:
                        continue 
                    b = solution[i][a]
                    d = solution[i][c]
                    if rnd_met[a][c] != -1 and rnd_met[a][c] != rnd_met[b][d]:
                        return False, f"Constaint (ii) not satisfied for players {a+1}, {b+1}, {c+1}, {d+1} in rounds {i+1} and {rnd_met[a][c]+1}", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT
 
    pairs = [
        (4, 3), (12, 3), (28, 3), (60, 3), # k <= 3
        (8, 6), (8, 7), (24, 7), (40, 6), (40, 7), # k <= 7
        (16, 14), (16, 15), (48, 6), (80, 4), # k <= 15
        (96, 3) # k <= 31, removed (32, 31) for too long output
    ]

    @staticmethod
    def generate() -> "Problem2006C5":
        # 15 manually picked diverse pairs where n*k is not much more than 300 
        n, k = random.choice(Problem2006C5.pairs)
        return Problem2006C5(n, k)

    def get_solution(self):
        return get_solution(self.n, self.k)
