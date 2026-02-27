from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["backups/problem_2009_4.py"]

import math
import random
import sympy
from fractions import Fraction
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_list_template
import itertools

FORMATTING = r"Output the answer as comma separated list inside of \boxed{...}. The first and second numbers in an answer should be the two factors of the palindrome product. The third number should be the palindrome product itself. For instance, \boxed{(3,3,9),(12,21,252)}."


def get_solution(k : int):
    division = k // 2 + 1
    sols = set()
    products = []
    for perm in itertools.product(range(3), repeat=division):
        number = int("".join(map(str, perm)))
        number_reverse = int("".join(map(str, perm[::-1])))
        product = number * number_reverse
        string_product = str(product)
        if len(string_product) == k and string_product == string_product[::-1] and string_product[-1] != 0:
            if product not in products:
                sols.add((number, number_reverse, product))
                products.append(product)
    return list(sols)

class ProblemDutch20094(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=FORMATTING,
        parameters=["k", "n"],
        source="Dutch Math Olympiad Finals 2009",
        problem_url="https://wiskundeolympiade.nl/files/opgaven/finale/2009/opgaven.pdf",
        solution_url="https://wiskundeolympiade.nl/files/opgaven/finale/2009/uitwerkingen.pdf",
        original_parameters={"n": 8, "k": 5},
        original_solution=get_solution(5),
    )
    k: int
    n: int

    def __init__(self, k: int, n: int):
        self.k = k
        self.n = n

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(k=self.k, n=self.n)
        
    def check(self, a: list[list[int]]) -> bool:
        check_format = self.check_format(a, is_integer=True, expected_length=self.n, is_unique=True, is_matrix=True)
        if not check_format[0]:
            return check_format
        all_good_solutions = set()
        for solution in a:
            if len(solution) != 3:
                return False, f"Each solution should have three numbers, but {solution} has {len(solution)}.", CheckerTag.INCORRECT_FORMAT
        check_format_2 = self.check_format([prod[2] for prod in a], is_unique=True)
        if not check_format_2[0]:
            return check_format_2
        for solution in a:
            str_0 = str(solution[0])
            str_1 = str(solution[1])
            str_2 = str(solution[2])
            if solution[0] * solution[1] == solution[2] and str_0 == str_1[::-1] and str_2 == str_2[::-1] and len(str_2) == self.k:
                all_good_solutions.add(solution[2])
            else:
                return False, f"{solution} is not a valid palindrome product.", CheckerTag.INCORRECT_SOLUTION
        if not len(all_good_solutions) == self.n:
            return False, f"You need to provide {self.n} palindrome products.", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "ProblemDutch20094":
        k = 2 * random.randint(3, 10) + 1
        min_sols = len(get_solution(k))
        n = random.randint(min(8, min_sols), min(50, min_sols))
        return ProblemDutch20094(k, n)
    
    def get_solution(self):
        return get_solution(self.k)[:self.n]
