from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["swiss/problem_2022_1_selection.py"]

import math
import random
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_list_template



def get_solution(n):
    def phi(n):
        amount = 0        
        for k in range(1, n + 1):
            if math.gcd(n, k) == 1:
                amount += 1
        return amount
    
    phi_n = phi(n)
    set_ = [k * phi_n for k in range(1, n + 1)]
    max_val = max(set_)
    return [1 if x in set_ else 0 for x in range(max_val + 1)][::-1]


class ProblemSwissSelection20221(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_list_template("Each number in the list should be either 0 or 1."),
        problem_url="https://mathematical.olympiad.ch/fileadmin/user_upload/Archiv/Intranet/Olympiads/Mathematics/deploy/exams/2022/Selection/MasterSolution/selectionSolution2022.pdf#page=1",
        solution_url="https://mathematical.olympiad.ch/fileadmin/user_upload/Archiv/Intranet/Olympiads/Mathematics/deploy/exams/2022/Selection/MasterSolution/selectionSolution2022.pdf#page=1",
        parameters=["n"],
        source="Swiss Math Olympiad IMO Selection 2022",
        original_parameters={"n": 16},
        original_solution=get_solution(16),
        tags=[Tag.IS_SIMPLIFIED, Tag.FIND_ANY, Tag.NUMBER_THEORY] 
    )
    n: int

    def __init__(self, n: int):
        self.n = n

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(n=self.n)
        
    def check(self, a: list[int]) -> bool:
        checker_format = self.check_format(a, min_val_inclusive=0, max_val_inclusive=1,
                                           is_integer=True)
        if not checker_format[0]:
            return checker_format
        for base in range(2, 100):
            number = sum(x * base ** i for i, x in enumerate(reversed(a)))
            if number % self.n != 0 or number == 0:
                return False, f"The number {number} is not divisible by {self.n} in base {base}.", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "ProblemSwissSelection20221":
        n = random.randint(11, 17)
        return ProblemSwissSelection20221(n)
    
    def get_solution(self):
        return get_solution(self.n)
