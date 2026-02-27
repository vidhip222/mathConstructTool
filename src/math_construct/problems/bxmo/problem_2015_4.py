from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["bxmo/problem_2015_4.py"]

import math
import random
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_matrix_template
from sympy import divisors
import numpy as np
LIST_FORMATTING_TEMPLATE = r"""Output the answer as a comma separated list of lists inside of \boxed{...}. For example \boxed{(1,2,3),(4,5,6),(7,8,9)}."""



def get_solution(n):
    return [
        [i, i + 1 * n, i + 2 * n] for i in range(1, n + 1)
    ]


class ProblemBxMO20154(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=LIST_FORMATTING_TEMPLATE,
        parameters=["n"],
        source="BxMO 2015 P4",
        original_parameters={"n": 15}, # not the original size, complexity is the same though
        problem_url="http://bxmo.org/problems/bxmo-problems-2015-zz.pdf",
        solution_url="http://bxmo.org/problems/bxmo-problems-2015-zz.pdf",
        original_solution=get_solution(15),
        tags=[Tag.IS_SIMPLIFIED, Tag.FIND_MAX_MIN, Tag.NUMBER_THEORY] 
    )
    n: int

    def __init__(self, n: int):
        self.n = n

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(n=self.n)
        
    def check(self, a: list[list[int]]) -> bool:
        flatted_list = [item for sublist in a for item in sublist]
        check, message, tag = self.check_format(flatted_list, is_integer=True, expected_length=3 * self.n, is_unique=True, 
                                                min_val_inclusive=1, max_val_inclusive=3 * self.n)
        if not check:
            return check, message, tag
        sum_diffs = 0
        for i in range(len(a)):
            if len(a[i]) < 3:
                return False, f"Arithmetic progression {a[i]} should have at least 3 elements.", CheckerTag.INCORRECT_SOLUTION
            diff = a[i][1] - a[i][0]
            sum_diffs += diff
            for j in range(len(a[i]) - 1):
                if a[i][j+1] - a[i][j] != diff:
                    return False, f"The arithmetic progression {a[i]} is not valid.", CheckerTag.INCORRECT_SOLUTION
        if not sum_diffs == self.n ** 2:
            return False, f"The sum of the common differences should be {self.n ** 2}, but is {sum_diffs}.", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @classmethod
    def generate_multiple_explicit(cls, n_problems: int = None) -> list["Problem"]:
        small = [1,2,3,4,5]
        mid = np.linspace(6, 20, 10).astype(int).tolist()
        big = np.linspace(21, 350, 9).astype(int).tolist()
        return [cls(n) for n in small + mid + big]

    @staticmethod
    def generate() -> "ProblemBxMO20154":
        n = random.randint(5, 20)
        return ProblemBxMO20154(n)
    
    def get_solution(self):
        return get_solution(self.n)
