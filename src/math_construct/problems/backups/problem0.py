from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["backups/problem0.py"]

import random
from math_construct.problems.problem import Problem, ProblemConfig, Tag
from math_construct.templates import get_matrix_template



class Problem0(Problem):
    """Dummy problem for testing."""
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_matrix_template(),
        parameters=["a", "b"],
        source="Dummy",
        original_parameters={"a": 2, "b": 2},
        original_solution=["11", "11"]
    )
    a: int
    b: int

    def __init__(self, a: int, b: int):
        self.a = a
        self.b = b

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(a=self.a, b=self.b)

    def check(self, solution: list[str]) -> bool:
        def is_prime(n: int) -> bool:   
            if n < 2:
                return False
            for i in range(2, int(n**0.5) + 1):
                if n % i == 0:
                    return False
            return True
        for i in range(self.a):
            for j in range(self.b):
                if not solution[i][j].isdigit() or int(solution[i][j]) < 1 or int(solution[i][j]) > 9:
                    return False
        for i in range(self.a):
            if not is_prime(int(solution[i])):
                return False
        for j in range(self.b):
            col = "".join([solution[i][j] for i in range(self.a)])
            if not is_prime(int(col)):
                return False
        return True

    @staticmethod
    def generate() -> "Problem0":
        a = random.randint(2, 3)        
        b = random.randint(2, 3)
        return Problem0(a, b)

    
