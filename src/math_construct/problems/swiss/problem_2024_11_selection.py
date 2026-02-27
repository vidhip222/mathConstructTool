from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["swiss/problem_2024_11_selection.py"]

import random
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag

LIST_FORMATTING_TEMPLATE = r"""Output the answer as a comma separated list of lists of coordinates inside of $\boxed{...}$. Each list contains 3 coordinates, indicating the x and y coordinates of the 3 squares that Nemo should pick. The rows are labeled from $0$ to $m-1$ and the columns are labeled from $0$ to $n-1$. For example, $\boxed{((1,1),(1,2),(1,3)),((1,2),(3,4),(5,6))}$ indicates that Nemo should first perform a move with the squares $(1,1), (1,2), (1,3)$ and then with the squares $(1,2),(3,4),(5,6)$."""


def moves_second_hypothesis(length_row):
    if length_row == 3:
        return [[0, 1, 2]]
    if length_row == 4:
        return [[0, 1, 2], [1, 2, 3]]
    if length_row % 2 == 0:
        moves = [[0, 1, length_row // 2 - 1], [length_row // 2, length_row - 2, length_row - 1]]
    else:
        moves = [[0, 1, length_row // 2], [length_row // 2, length_row - 2, length_row - 1]]
    moves = moves + 2 * [[x + 1 for x in move] for move in moves_second_hypothesis(length_row - 2)]
    return moves

def moves_one_row(length_row):
    if length_row == 3:
        return [[0, 1, 2]]
    if length_row == 4:
        return [[0, 1, 2], [1, 2, 3]]

    moves_first = [[x + 1 for x in move] for move in moves_one_row(length_row - 2)]
    moves = moves_first + moves_second_hypothesis(length_row)
    return moves

def get_solution(n, m):
    moves = []
    for row in range(m):
        moves_row = moves_one_row(n)
        moves = moves + [[(row, x) for x in move] for move in moves_row]

    range_ =[n // 2] if n % 2 == 1 else [n // 2, n // 2 - 1]
    number = n if n % 2 == 1 else n // 2
    for col in range_:
        for _ in range(number):
            moves_one = moves_one_row(m)
            moves = moves + [[(x, col) for x in move] for move in moves_one]

    return moves

class ProblemSwissSelection202411(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=LIST_FORMATTING_TEMPLATE,
        parameters=["m", "n", "max_moves"],
        problem_url="https://mathematical.olympiad.ch/fileadmin/user_upload/Archiv/Intranet/Olympiads/Mathematics/deploy/exams/2024/Selection/MasterSolution/selectionSolution2024.pdf#page=32",
        solution_url="https://mathematical.olympiad.ch/fileadmin/user_upload/Archiv/Intranet/Olympiads/Mathematics/deploy/exams/2024/Selection/MasterSolution/selectionSolution2024.pdf#page=32",
        source="Swiss Math Olympiad IMO Selection 2024",
        original_parameters={"m": 4, "n": 4, "max_moves": 16},
        original_solution=get_solution(4, 4),
        tags=[Tag.IS_SIMPLIFIED, Tag.IS_ORIGINAL, Tag.FIND_MAX_MIN, Tag.COMBINATORICS]  
    )
    m: int
    n: int
    max_moves: int

    def __init__(self, m: int, n: int, max_moves: int):
        self.m = m
        self.n = n
        self.max_moves = max_moves

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(m=self.m, n=self.n, max_moves=self.max_moves)
    
    def is_collinear(self, a: tuple[int, int], b: tuple[int, int], c: tuple[int, int]) -> bool:
        x1, y1 = a
        x2, y2 = b
        x3, y3 = c
        return (x1 - x2) * (y1 - y3) == (x1 - x3) * (y1 - y2)
    
    def get_middle(self, a: tuple[int, int], b: tuple[int, int], c: tuple[int, int]) -> tuple[int, int]:
        if a[0] < b[0] < c[0] or c[0] < b[0] < a[0] or a[1] < b[1] < c[1] or c[1] < b[1] < a[1]:
            return b
        if a[0] < c[0] < b[0] or b[0] < c[0] < a[0] or a[1] < c[1] < b[1] or b[1] < c[1] < a[1]:
            return c
        if b[0] < a[0] < c[0] or c[0] < a[0] < b[0] or b[1] < a[1] < c[1] or c[1] < a[1] < b[1]:
            return a

        
    def check(self, a: list[list[list[int]]]) -> bool:
        checker_format = self.check_format(a, expected_length=self.max_moves, is_integer=True,
                                           is_matrix=True, min_val_inclusive=0, 
                                           max_val_inclusive=max(self.m - 1, self.n - 1))
        if not checker_format[0]:
            return checker_format
        current_board = [
            [1 for _ in range(self.n)]
            for _ in range(self.m)
        ]
        for move in a:
            if len(move) != 3:
                return False, f"Expected 3 squares, got {len(move)}.", CheckerTag.INCORRECT_FORMAT
            for square in move:
                if len(square) != 2:
                    return False, f"Expected 2 coordinates, got {len(square)}.", CheckerTag.INCORRECT_FORMAT
                x, y = square
                if x < 0 or x >= self.m or y < 0 or y >= self.n:
                    return False, f"Invalid coordinates {x}, {y}.", CheckerTag.INCORRECT_FORMAT
        for move in a:
            if not self.is_collinear(move[0], move[1], move[2]):
                return False, f"Squares {move[0]}, {move[1]}, {move[2]} are not collinear.", CheckerTag.INCORRECT_SOLUTION
            middle = self.get_middle(move[0], move[1], move[2])
            left = move[0] if move[0] != middle else move[1]
            right = move[2] if move[2] != middle else move[1]
            if current_board[left[0]][left[1]] == 0 or current_board[right[0]][right[1]] == 0:
                return False, f"Squares {left}, {right} are empty for move {move}.", CheckerTag.INCORRECT_SOLUTION
            current_board[left[0]][left[1]] -= 1
            current_board[right[0]][right[1]] -= 1
            current_board[middle[0]][middle[1]] += 2
        return True, "OK", CheckerTag.CORRECT     

    @classmethod
    def g(cls, integer):
        if integer % 2 == 0:
            return 2 * (2 ** (integer // 2) - 1) - integer
        else:
            return 3 * (2 ** ((integer - 1) // 2) - 1) - integer + 1

    @staticmethod
    def generate() -> "ProblemSwissSelection202411":
        m = random.randint(4, 6)
        n = random.randint(4, 6)
        while n == 6 and m == 6:
            m = random.randint(4, 6)
            n = random.randint(4, 6)
        max_moves = n * ProblemSwissSelection202411.g(m) + m * ProblemSwissSelection202411.g(n)
        return ProblemSwissSelection202411(m, n, max_moves)

    def get_solution(self):
        return get_solution(self.n, self.m)
