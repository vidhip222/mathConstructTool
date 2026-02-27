import random
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_matrix_template
from math_construct.utils import get_latex_array

TEMPLATE_PROBLEM = """Fill each unshaded cell of the {n_rows}x{n_cols} grid with a number that is either 1, 3, or 5. For each
cell, exactly one of the touching cells must contain the same number. Here touching includes
cells that only share a point, i.e. touch diagonally.

The grid is:
$$
{init_grid}
$$

o - unshaded cell
x - shaded cell
"""

# We generate 100 variations and then hard-code them for fast sampling
VARIATIONS = [
    {"n_rows": 5, "n_cols": 5, "init_grid": ['xx3x3', 'xoooo', 'xxxxx', 'o3xoo', 'x1ooo']},
    {"n_rows": 6, "n_cols": 4, "init_grid": ['oxo3', 'x1xo', 'xxox', '3oxo', 'xxxo', 'xx11']},
    {"n_rows": 4, "n_cols": 6, "init_grid": ['1oxxox', 'xoo15o', 'xxoxoo', 'xxx5xx']},
    {"n_rows": 5, "n_cols": 5, "init_grid": ['xox1x', 'ooooo', 'xxxxo', 'xxxox', 'oox1x']},
    {"n_rows": 4, "n_cols": 6, "init_grid": ['x1xxxx', '3ooxxo', 'ox3o5o', '11x1xo']},
    {"n_rows": 6, "n_cols": 5, "init_grid": ['oo3xx', 'oooox', 'xxxo5', '5oxx5', 'ooxo3', '1oxoo']},
    {"n_rows": 5, "n_cols": 4, "init_grid": ['oox3', 'ooxo', 'xoxx', '1xox', 'xooo']},
    {"n_rows": 4, "n_cols": 4, "init_grid": ['ooox', '1oxo', 'ooxo', 'xoxx']},
    {"n_rows": 4, "n_cols": 5, "init_grid": ['oooox', 'xxxxo', 'xxooo', 'xoxox']},
    {"n_rows": 4, "n_cols": 4, "init_grid": ['x1oo', 'ooxo', 'xxox', 'ooox']},
    {"n_rows": 5, "n_cols": 4, "init_grid": ['xxoo', 'xx1x', 'xoxo', 'oooo', 'oxo3']},
    {"n_rows": 5, "n_cols": 4, "init_grid": ['x1oo', 'xx5o', 'xooo', '3oxo', 'xxx3']},
    {"n_rows": 4, "n_cols": 5, "init_grid": ['xooox', 'oxxo1', 'xxooo', 'xo3ox']},
    {"n_rows": 4, "n_cols": 4, "init_grid": ['xxxx', 'o5xo', 'ooo5', 'xooo']},
    {"n_rows": 5, "n_cols": 5, "init_grid": ['xxox3', 'xxoxo', 'xxo11', '15oox', 'x1xxx']},
    {"n_rows": 4, "n_cols": 6, "init_grid": ['5o1ooo', 'oo3oxo', 'xxxxx5', 'xooxoo']},
    {"n_rows": 4, "n_cols": 6, "init_grid": ['x1xxx3', '51xxxo', '3oxxoo', '3oo5ox']},
    {"n_rows": 4, "n_cols": 4, "init_grid": ['11xo', 'xx3o', 'ooo5', '5x1o']},
    {"n_rows": 4, "n_cols": 4, "init_grid": ['oxo5', 'o5oo', 'xoxx', 'ooxx']},
    {"n_rows": 5, "n_cols": 4, "init_grid": ['xx3x', '5oxo', '1x11', 'oxox', 'xxxo']},
    {"n_rows": 4, "n_cols": 5, "init_grid": ['oxoox', 'oxoxx', 'oxooo', 'oxxoo']},
    {"n_rows": 4, "n_cols": 7, "init_grid": ['xo3x33x', 'oxxox1o', 'ooo1xoo', '53xo5xx']},
    {"n_rows": 4, "n_cols": 4, "init_grid": ['11xo', 'xx3o', 'ooo5', '5x1o']},
    {"n_rows": 4, "n_cols": 4, "init_grid": ['xo5x', 'xxoo', 'oxoo', 'oxoo']},
    {"n_rows": 5, "n_cols": 4, "init_grid": ['oo5x', 'oxo1', '5xoo', 'xxox', 'xoox']},
    {"n_rows": 5, "n_cols": 4, "init_grid": ['o5xx', 'ooo3', 'xxxx', 'x1oo', 'x315']},
    {"n_rows": 4, "n_cols": 5, "init_grid": ['xx55x', 'xxxoo', 'oooox', 'oooxo']},
    {"n_rows": 5, "n_cols": 5, "init_grid": ['xoxoo', 'ooxoo', 'o1xx3', 'xooox', 'x5xxx']},
    {"n_rows": 5, "n_cols": 4, "init_grid": ['ooxx', 'xxx5', 'ooxo', 'oxox', 'ox1x']},
    {"n_rows": 5, "n_cols": 4, "init_grid": ['5xxx', 'oxxo', 'xxox', 'o5ox', 'xoxx']},
    {"n_rows": 4, "n_cols": 6, "init_grid": ['ooo1ox', 'oox3xx', 'ooxxoo', 'xooxoo']},
    {"n_rows": 6, "n_cols": 4, "init_grid": ['ooxx', 'ooo3', 'x1ox', 'xxxo', 'oxox', 'x3xx']},
    {"n_rows": 4, "n_cols": 6, "init_grid": ['1oxxox', 'xoo15o', 'xxoxoo', 'xxx5xx']},
    {"n_rows": 4, "n_cols": 6, "init_grid": ['x1xxxx', '3ooxxo', 'ox3o5o', '11x1xo']},
    {"n_rows": 4, "n_cols": 4, "init_grid": ['33xx', '51o5', '5xox', '3o1o']},
    {"n_rows": 6, "n_cols": 4, "init_grid": ['xxxx', 'o13x', 'oxoo', 'oxox', 'ox3o', 'x1oo']},
    {"n_rows": 4, "n_cols": 4, "init_grid": ['ooox', 'xxxo', 'xoxx', 'oxxx']},
    {"n_rows": 4, "n_cols": 4, "init_grid": ['5oo3', 'x1ox', 'xxoo', 'o1oo']},
    {"n_rows": 4, "n_cols": 4, "init_grid": ['o35x', 'ooox', 'xxoo', 'xx5o']},
    {"n_rows": 4, "n_cols": 4, "init_grid": ['x1oo', 'ooxo', 'xxox', 'ooox']},
    {"n_rows": 4, "n_cols": 4, "init_grid": ['xxxx', 'o5xo', 'ooo5', 'xooo']},
    {"n_rows": 5, "n_cols": 4, "init_grid": ['xoxx', '3x1x', '5xx1', 'ooox', 'xxoo']},
    {"n_rows": 4, "n_cols": 4, "init_grid": ['xooo', 'ooo1', '33xo', '55xx']},
    {"n_rows": 5, "n_cols": 4, "init_grid": ['5ooo', 'x53x', '3oox', 'ooxo', '5x5x']},
    {"n_rows": 6, "n_cols": 4, "init_grid": ['xxxx', 'o13x', 'oxoo', 'oxox', 'ox3o', 'x1oo']},
    {"n_rows": 5, "n_cols": 5, "init_grid": ['xooxx', 'ooxxx', 'xx1o3', 'ooxoo', 'x33xo']},
    {"n_rows": 4, "n_cols": 4, "init_grid": ['xoo1', 'ox3x', 'oo5o', 'oox1']},
    {"n_rows": 5, "n_cols": 4, "init_grid": ['xxoo', 'xx1x', 'xoxo', 'oooo', 'oxo3']},
    {"n_rows": 4, "n_cols": 4, "init_grid": ['xooo', '5xox', 'oo31', 'xo3o']},
    {"n_rows": 4, "n_cols": 6, "init_grid": ['x1xxxx', '3ooxxo', 'ox3o5o', '11x1xo']},
    {"n_rows": 4, "n_cols": 6, "init_grid": ['xxx1oo', '5xoooo', 'oooox3', 'oo3o5x']},
    {"n_rows": 4, "n_cols": 6, "init_grid": ['5o1ooo', 'oo3oxo', 'xxxxx5', 'xooxoo']},
    {"n_rows": 4, "n_cols": 5, "init_grid": ['xx3xo', 'oo1oo', '1xoxo', 'x3o5o']},
    {"n_rows": 4, "n_cols": 4, "init_grid": ['oox5', 'x1xo', '1xo1', 'xxo3']},
    {"n_rows": 6, "n_cols": 4, "init_grid": ['xx3x', 'x3xx', 'ooxo', 'oooo', 'xoox', 'xo5o']},
    {"n_rows": 6, "n_cols": 5, "init_grid": ['oxo5x', 'o3xxo', 'xoooo', 'oxxxo', 'xoxxx', 'x1xo1']},
    {"n_rows": 5, "n_cols": 4, "init_grid": ['x33o', 'oxox', 'x1xx', 'xxoo', 'xoxo']},
    {"n_rows": 4, "n_cols": 4, "init_grid": ['xoox', 'oxxo', 'o3ox', 'o15x']},
    {"n_rows": 5, "n_cols": 4, "init_grid": ['x5xx', 'oooo', 'xxxo', 'ooxo', 'ooxo']},
    {"n_rows": 4, "n_cols": 6, "init_grid": ['ooo1ox', 'oox3xx', 'ooxxoo', 'xooxoo']},
    {"n_rows": 5, "n_cols": 5, "init_grid": ['xxox3', 'xxoxo', 'xxo11', '15oox', 'x1xxx']},
    {"n_rows": 5, "n_cols": 4, "init_grid": ['oxxx', 'oxox', 'xooo', 'oxxx', 'oxxx']},
    {"n_rows": 5, "n_cols": 4, "init_grid": ['1oxx', 'ooxx', 'xoox', 'xxox', 'xooo']},
    {"n_rows": 5, "n_cols": 4, "init_grid": ['xoxx', '3x1x', '5xx1', 'ooox', 'xxoo']},
    {"n_rows": 4, "n_cols": 4, "init_grid": ['xxox', 'xoox', '1x3x', 'xooo']},
    {"n_rows": 4, "n_cols": 4, "init_grid": ['33xx', '51o5', '5xox', '3o1o']},
    {"n_rows": 5, "n_cols": 4, "init_grid": ['oo1x', 'ooxo', 'xoo5', '5oxo', 'x5ox']},
    {"n_rows": 6, "n_cols": 4, "init_grid": ['3oxx', '5oox', 'oxo5', 'ooox', 'xox5', 'xxxo']},
    {"n_rows": 5, "n_cols": 4, "init_grid": ['5x1o', 'xoxx', 'xxoo', 'oxo1', 'ooox']},
    {"n_rows": 4, "n_cols": 4, "init_grid": ['oo5o', 'oxxx', 'ooxx', 'oxxx']},
    {"n_rows": 4, "n_cols": 5, "init_grid": ['xx3xo', 'xo3xo', 'x1xox', 'x5o1x']},
    {"n_rows": 5, "n_cols": 4, "init_grid": ['ooxx', 'ooxx', 'xxo3', 'xxxo', '5ox1']},
    {"n_rows": 4, "n_cols": 4, "init_grid": ['o13o', '5x5x', 'oxox', 'oooo']},
    {"n_rows": 4, "n_cols": 4, "init_grid": ['oxo5', 'o5oo', 'xoxx', 'ooxx']},
    {"n_rows": 5, "n_cols": 4, "init_grid": ['ooxx', 'oox5', 'xxxo', 'ooxo', 'oo1x']},
    {"n_rows": 4, "n_cols": 5, "init_grid": ['xx55x', 'xxxoo', 'oooox', 'oooxo']},
    {"n_rows": 4, "n_cols": 4, "init_grid": ['xxxx', 'o5xo', 'ooo5', 'xooo']},
    {"n_rows": 4, "n_cols": 4, "init_grid": ['1o1x', 'oxoo', '3x5x', '3xxo']},
    {"n_rows": 4, "n_cols": 6, "init_grid": ['xxoooo', 'oxooxx', 'oxxooo', 'xxxoo3']},
    {"n_rows": 4, "n_cols": 4, "init_grid": ['ooxx', 'oxx1', 'x3xo', 'xx55']},
    {"n_rows": 4, "n_cols": 5, "init_grid": ['oooox', 'xxxxo', 'xxooo', 'xoxox']},
    {"n_rows": 5, "n_cols": 4, "init_grid": ['xx3x', '5oxo', '1x11', 'oxox', 'xxxo']},
    {"n_rows": 4, "n_cols": 5, "init_grid": ['xooox', 'oxxo1', 'xxooo', 'xo3ox']},
    {"n_rows": 5, "n_cols": 5, "init_grid": ['xoxoo', 'ooxoo', 'o1xx3', 'xooox', 'x5xxx']},
    {"n_rows": 5, "n_cols": 4, "init_grid": ['xooo', 'oxoo', 'xxox', '3oo1', '3oxo']},
    {"n_rows": 5, "n_cols": 4, "init_grid": ['o1oo', 'xxo3', 'xx1o', '5x5x', '5xox']},
    {"n_rows": 4, "n_cols": 4, "init_grid": ['ooox', 'ooxo', 'xooo', 'xoo3']},
    {"n_rows": 4, "n_cols": 4, "init_grid": ['oo5o', 'oxxx', 'ooxx', 'oxxx']},
    {"n_rows": 5, "n_cols": 4, "init_grid": ['o5xx', 'ooo3', 'xxxx', 'x1oo', 'x315']},
    {"n_rows": 4, "n_cols": 4, "init_grid": ['5x3o', '5xxx', 'xxx3', '5oox']},
    {"n_rows": 5, "n_cols": 4, "init_grid": ['xooo', 'oxoo', 'oo15', 'ooxx', 'xxoo']},
    {"n_rows": 4, "n_cols": 5, "init_grid": ['xx5ox', 'xxx1o', '3oxoo', 'xooxx']},
    {"n_rows": 4, "n_cols": 4, "init_grid": ['ooox', 'ooxo', 'xooo', 'xoo3']},
    {"n_rows": 4, "n_cols": 5, "init_grid": ['x55oo', 'xx11o', 'ooxo5', 'xxxxo']},
    {"n_rows": 4, "n_cols": 4, "init_grid": ['xoox', 'oxxx', '3ooo', 'ooox']},
    {"n_rows": 4, "n_cols": 4, "init_grid": ['x3o5', 'xxox', 'oxx1', 'oxx1']},
    {"n_rows": 6, "n_cols": 4, "init_grid": ['xoox', 'xoox', 'o15o', 'oxxo', 'ox33', '5x1o']},
    {"n_rows": 4, "n_cols": 4, "init_grid": ['oxoo', 'oxo5', 'oxx1', 'oxox']},
    {"n_rows": 5, "n_cols": 4, "init_grid": ['oxxo', 'xoxo', 'oxxx', '5xoo', '1ooo']},
    {"n_rows": 4, "n_cols": 4, "init_grid": ['1o1x', 'oxoo', '3x5x', '3xxo']},
]

class Problem1(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=TEMPLATE_PROBLEM,
        formatting_instructions=get_matrix_template(),
        parameters=["n_rows", "n_cols", "init_grid"],
        source="USAMTS 23/24 Round 1",
        original_parameters={
            "n_rows": 7,
            "n_cols": 7,
            "init_grid": ["ooooooo", "1o1o3o5", "oooxooo", "xo1135o", "ooooxox", "oxooooo", "5oo5ooo"],
        },
        original_solution=["5335535", "1511315", "133x513", "x511353", "3353x1x", "5x11515", "5335335"],
        problem_url="https://files.usamts.org/Problems_35_1.pdf",
        solution_url="https://files.usamts.org/Solutions_35_1.pdf",
        tag=[Tag.PUZZLE, Tag.IS_ORIGINAL, Tag.IS_GENERALIZED, Tag.FIND_ANY]
    )
    n_rows: int
    n_cols: int
    init_grid: list[str]
    
    def __init__(self, n_rows: int, n_cols: int, init_grid: list[str]):
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.init_grid = init_grid

    def get_problem(self):
        latex_grid = get_latex_array(self.init_grid)
        return TEMPLATE_PROBLEM.format(n_rows=self.n_rows, n_cols=self.n_cols, init_grid=latex_grid)

    @staticmethod
    def generate() -> "Problem1":
        # For speed returns one of the hard-coded generations generated by the code below 
        variation = random.choice(VARIATIONS)
        n_rows, n_cols, init_grid = variation["n_rows"], variation["n_cols"], variation["init_grid"]
        return Problem1(n_rows, n_cols, init_grid)
        # while True:
        #     n_rows = random.randint(4, 8)
        #     n_cols = random.randint(4, 8)
        #     for _ in range(100000):
        #         answer, grid = [], []
        #         for _ in range(n_rows):
        #             curr_row, init_row = "", ""
        #             for _ in range(n_cols):
        #                 z = random.choice(["1", "3", "5", "x"])
        #                 curr_row += z
        #                 # with some probability keep the current letter, otherwise replace it with o or x
        #                 init_row += z if random.random() < 0.3 else ("o" if z != "x" else "x") 
        #             grid.append(init_row)
        #             answer.append(curr_row)
        #         problem = Problem1(n_rows, n_cols, grid)
        #         problem.set_solution(answer)
        #         if problem.check_raw(answer):
        #             return problem

    def check(self, answer) -> bool:
        # First, check if the answer is a valid grid 
        if len(answer) != self.n_rows:
            return False, f"List of size {len(answer)}, should be {self.n_rows}", CheckerTag.INCORRECT_LENGTH
        for row in answer:
            if len(row) != self.n_cols:
                return False, f"Row of size {len(row)}, should be {self.n_cols}", CheckerTag.INCORRECT_LENGTH

        # Check if the individual cells are valid
        for i in range(self.n_rows):
            for j in range(self.n_cols):
                if self.init_grid[i][j] == "o" and answer[i][j] not in ["1", "3", "5", "x"]:
                    return False, f"Cell ({i}, {j}) is unshaded and has value {answer[i][j]}, should be 1, 3, 5, or x", CheckerTag.INCORRECT_FORMAT
                if self.init_grid[i][j] != "o" and answer[i][j] != self.init_grid[i][j]:
                    return False, f"Cell ({i}, {j}) is shaded and has value {answer[i][j]}, should be {self.init_grid[i][j]}", CheckerTag.INCORRECT_SOLUTION

        # Check the touching cells for each cell
        for i in range(self.n_rows):
            for j in range(self.n_cols):
                if self.init_grid[i][j] == "x":
                    continue
                nums = []
                for i2 in range(self.n_rows):
                    for j2 in range(self.n_cols):
                        if abs(i - i2) <= 1 and abs(j - j2) <= 1:
                            nums.append(answer[i2][j2])
                k = sum([x == answer[i][j] for x in nums])
                if k != 2:
                    return False, f"Cell ({i}, {j}) has {k} touching cells with the same value, should be 2", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT
