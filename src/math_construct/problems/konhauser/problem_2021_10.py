from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["konhauser/problem_2021_10.py"]

import random
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_list_template
import itertools


def get_solution(l, k, m):
    max_n_digits_binary = len(bin(10**l)) - 2
    min_n_digits_binary = len(bin(10**(l - 1))) - 2
    solutions = set()
    for digits in range(min_n_digits_binary + 1, max_n_digits_binary):
        if digits - k < 0:
            continue
        for positions in itertools.combinations(range(digits), k - 1):
            # Initialize a list of '0's
            binary = ['0'] * digits
            # Set '1's in the specified positions
            for pos in positions:
                binary[pos] = '1'
            # Convert the list to a string
            binary_str = ''.join(["1"] + binary)
            n = int(binary_str, 2)
            if len(str(n)) == l and n not in solutions:
                solutions.add(n)
                if len(solutions) >= m:
                    return list(solutions)
   
    return list(solutions)

class ProblemKonhauser202110(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_list_template(),
        parameters=["l", "k", "m"],
        problem_url="https://drive.google.com/file/d/1yC9Kn09fJY1pwT0Dn4fh-ywhwBv-lXD1/view", # page 9
        solution_url="https://drive.google.com/file/d/1yC9Kn09fJY1pwT0Dn4fh-ywhwBv-lXD1/view", # page 9
        source="Konhauser Problemfest 2021 P10",
        original_parameters={"k": 10, "l": 10, "m": 5},
        original_solution=get_solution(10, 10, 5),
        tags=[Tag.IS_ORIGINAL, Tag.ALGEBRA, Tag.FIND_MAX_MIN, Tag.IS_GENERALIZED]
    )
    l: int
    k: int
    m: int

    def __init__(self, l: int, k: int, m: int):
        self.l = l
        self.k = k
        self.m = m

    def get_problem(self):
        stmt = PROBLEM_TEMPLATE.format(l=self.l, k=self.k, m=self.m, k_plus_1=self.k + 1)
        if self.m == 1: 
            stmt = stmt.replace("numbers", "number")
            stmt = stmt.replace("distinct ", "")
        return stmt

    def check(self, a: list[int]) -> bool:
        checker_format = self.check_format(a, expected_length=self.m, min_val_exclusive=0, is_integer=True, is_unique=True)
        if not checker_format[0]:
            return checker_format
        for n in a:
            if len(str(n)) != self.l:
                return False, f"The number should have {self.l} digits.", CheckerTag.INCORRECT_SOLUTION
            binary = bin(n)
            # this allows us to not have to compute the binomial coefficient, thus more stable
            n_ones = binary.count("1")
            if n_ones != self.k:
                return False, f"The number {n} is divisible by exactly 2^{n_ones}.", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT
        
    @staticmethod
    def generate() -> "ProblemKonhauser202110":
        l = random.randint(8, 30)
        length_bin = len(bin(10**l)) - 2
        k = random.randint(3, length_bin - 2)
        if k == length_bin - 1:
            m = random.randint(3, length_bin - 2)
        else:
            m = random.randint(5, 20)
        return ProblemKonhauser202110(l, k, m)
    
    def get_solution(self):
        return get_solution(self.l, self.k, self.m)
