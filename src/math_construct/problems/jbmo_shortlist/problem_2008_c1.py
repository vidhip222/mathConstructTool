from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["jbmo_shortlist/problem_2008_c1.py"]

import random
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
import numpy as np


EXTRA_FORMATTING_INSTRUCTIONS = r"""As your output, present a tuple of 2 lists. The first list should be a list of 1-indexed coordinates for where the white markers were initially placed. The second one should contain a sequence of quadruples in the form $(a,b,c,d)$, which represent a coloring of the marker at coordinates $(a,b)$, which is then placed at a valid position $(c,d)$. Output the answer as 2 comma-separated lists of comma-separated tuples in in $\boxed{...}$. For example, for a $3\times 3$ board: $\boxed{([(1, 1), (1,2)], [(1,1,3,3), (1,2,1,1)])}$"""

def get_solution(N:int) -> tuple[list[tuple[int]], list[tuple[int]]]:
    coords = [(i+1, j+1) for i in range(N) for j in range(N-1)]
    seq = [(i+1, j+1, i+1, j+2) for j in range(N-1)[::-1] for i in range(N)[::-1]]
    return (coords, seq)

class ProblemJBMO2008C1(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=EXTRA_FORMATTING_INSTRUCTIONS,
        parameters=["N"],
        source="2008 JBMO Shortlist C1",
        original_parameters={"N": 5},
        original_solution=get_solution(5),
        problem_url="https://artofproblemsolving.com/community/c6h1528878p9182667",
        solution_url="https://artofproblemsolving.com/community/c6h1528878p9182667",
        tags=[Tag.COMBINATORICS, Tag.IS_GENERALIZED, Tag.FIND_MAX_MIN]
    )
    N: int

    def __init__(self, N: int):
        self.N = N

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(N=self.N, n=(self.N*(self.N-1)))

    def check(self, x: tuple[list[tuple[int]], list[tuple[int]]]) -> bool:

        if len(x) != 2:
            return False, f"Example should contain 2 sequences - 1 of coordinates, and 1 of moves", CheckerTag.INCORRECT_LENGTH
        
        coords = x[0]
        seq = x[1]
        state = [['e' for _ in range(self.N)] for _ in range(self.N)]

        for i, coord in enumerate(coords):
            if len(coord) != 2:
                return False, f"Each coordinate should contain 2 entries", CheckerTag.INCORRECT_FORMAT
            
            coords[i] = tuple(coord)

            if coord[0] <= 0 or coord[0] > self.N or coord[1] <= 0 or coord[0] > self.N:
                return False, f"Coordinates {coord} are invalid for a ${self.N}\\times{self.N}$ board.", CheckerTag.INCORRECT_FORMAT
            
            state[coord[0] - 1][coord[1] - 1] = 'w'

        if len(set(coords)) != len(coords):
            return False, f"Set of coordinates should contain unique marker positions", CheckerTag.INCORRECT_FORMAT
        
        if len(coords) != self.N*(self.N - 1):
            return False, "Number of white markers is incorrect", CheckerTag.INCORRECT_FORMAT
        
        if len(coords) != len(seq):
            return False, f'Number of coordinate entries should equal the number of move entries', CheckerTag.INCORRECT_FORMAT

        for move in seq:
            if len(move) != 4:
                return False, f"Each move should contain 4 entries", CheckerTag.INCORRECT_FORMAT
            if move[0] <= 0 or move[0] > self.N or move[1] <= 0 or move[0] > self.N or\
               move[2] <= 0 or move[2] > self.N or move[3] <= 0 or move[3] > self.N:
                return False, f"Move {move} is invalid for a ${self.N}\\times{self.N}$ board.", CheckerTag.INCORRECT_FORMAT
            
            if not (move[0], move[1]) in coords or state[move[0] - 1][move[1] - 1] != 'w':
                return False, f"White marker with coordinates {(move[0], move[1])} for state {state} does not exist.", CheckerTag.INCORRECT_SOLUTION
            
            if state[move[2] - 1][move[3] - 1] != 'e':
                return False, f"Position at {(move[2], move[3])} is non-empty", CheckerTag.INCORRECT_SOLUTION
            
            if move[2] > 1 and state[move[2] - 2][move[3] - 1] == 'w' and (move[2]-1 != move[0] or move[3] != move[1]):
                return False, f'Move {move} places a marker next to a white neighbor', CheckerTag.INCORRECT_SOLUTION
            if move[3] > 1 and state[move[2] - 1][move[3] - 2] == 'w' and (move[2] != move[0] or move[3]-1 != move[1]):
                return False, f'Move {move} places a marker next to a white neighbor', CheckerTag.INCORRECT_SOLUTION
            if move[2] < self.N and state[move[2]][move[3] - 1] == 'w' and (move[2]+1 != move[0] or move[3] != move[1]):
                return False, f'Move {move} places a marker next to a white neighbor', CheckerTag.INCORRECT_SOLUTION
            if move[3] < self.N and state[move[2] - 1][move[3]] == 'w' and (move[2] != move[0] or move[3]+1 != move[1]):
                return False, f'Move {move} places a marker next to a white neighbor', CheckerTag.INCORRECT_SOLUTION
            
            state[move[0] - 1][move[1] - 1] = 'e'
            state[move[2] - 1][move[3] - 1] = 'b'
        
        if (np.array(state) == 'b').sum() != self.N*(self.N-1) or (np.array(state) == 'e').sum() != self.N or (np.array(state) == 'w').sum() != 0:
            return False, 'Move set was invalid or not all white markers were moved', CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "ProblemJBMO2008C1":
        N = random.randint(5, 9)
        return ProblemJBMO2008C1(N)

    def get_solution(self):
        return get_solution(self.N)
