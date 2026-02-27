from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["backups/problem_1998_1_3.py"]

import random
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.utils import convert_to_int, get_latex_array
from math_construct.templates import get_matrix_template


FULL_SOLUTION = [["1", "13", "3", "15"], ["11", "9", "7", "5"], ["12", "2", "14", "4"]]

class Problem4(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_matrix_template(),
        parameters=["init_grid"],
        source="USAMTS 98/99 Round 1",
        original_parameters={"init_grid": [["1", "o", "o", "o"], ["o", "9", "o", "5"], ["o", "o", "14", "o"]]},
        original_solution=FULL_SOLUTION,
        problem_url="https://files.usamts.org/Problems_10_1.pdf",
        solution_url="https://files.usamts.org/Solutions_10_1.pdf",
        tag=[Tag.PUZZLE, Tag.FIND_ANY, Tag.IS_ORIGINAL, Tag.IS_GENERALIZED]
    )
    init_grid: list[list[str]]

    def __init__(self, init_grid: list[list[str]]):
        self.init_grid = init_grid

    def get_problem(self):
        latex_grid = get_latex_array(self.init_grid)
        return PROBLEM_TEMPLATE.format(init_grid=latex_grid)

    def check(self, solution: list[list[str]]):
        try:
            solution = convert_to_int(solution)
        except Exception:
            return False, "Could not convert solution to integers", CheckerTag.INCORRECT_FORMAT

        if len(solution) != 3:
            return False, f"List of size {len(solution)}, should be 3", CheckerTag.INCORRECT_LENGTH
        rem = set([1, 2, 3, 4, 5, 7, 9, 10, 11, 12, 13, 14, 15])
        for i in range(3):
            if len(solution[i]) != 4:
                return False, f"Row {i} of size {len(solution[i])}, should be 4", CheckerTag.INCORRECT_LENGTH
            for j in range(4):
                if solution[i][j] not in rem:
                    return False, f"Value from cell ({i},{j}) not in the allowed set", CheckerTag.INCORRECT_SOLUTION
                rem.remove(solution[i][j])
                if self.init_grid[i][j] != "o" and solution[i][j] != int(self.init_grid[i][j]):
                    return False, f"Value from cell ({i},{j}) differs from the initial grid", CheckerTag.INCORRECT_SOLUTION
        if len(rem) != 1:
            return False, f"Not all values have been used", CheckerTag.INCORRECT_SOLUTION

        res = set()
        for i in range(3):
            if (row_sum := sum(solution[i])) % 4 != 0:
                return False, f"Sum of row {i} is {row_sum}, should be divisible by 4", CheckerTag.INCORRECT_SOLUTION
            res.add(row_sum // 4)

        for i in range(4):
            if (col_sum := sum(solution[j][i] for j in range(3))) % 3 != 0:
                return False, f"Sum of column {i} is {col_sum}, should be divisible by 3", CheckerTag.INCORRECT_SOLUTION
            res.add(col_sum // 3)

        return len(res) == 1, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "Problem4":
        # We can repeatedly swap two columns or two rows to generate new problems
        init_grid, solution = Problem4.config.original_parameters["init_grid"], Problem4.config.original_solution
        for _ in range(100):
            swap_axis = random.randint(0, 1)
            if swap_axis == 0:
                i, j = random.randint(0, len(solution) - 1), random.randint(0, len(solution) - 1)
                solution[i], solution[j] = solution[j], solution[i]
                init_grid[i], init_grid[j] = init_grid[j], init_grid[i]
            else:
                i, j = random.randint(0, len(solution[0]) - 1), random.randint(0, len(solution[0]) - 1)
                for row in solution:
                    row[i], row[j] = row[j], row[i]
                for row in init_grid:
                    row[i], row[j] = row[j], row[i]
        new_problem = Problem4(init_grid=init_grid)
        new_problem.set_solution(solution)
        assert new_problem.check_raw(new_problem.get_solution())
        return new_problem


