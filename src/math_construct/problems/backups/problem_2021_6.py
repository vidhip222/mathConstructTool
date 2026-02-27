from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["backups/problem_2021_6.py"]

import random
import sympy
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.utils import latex2sympy_fixed


def get_solution(n, k, m):
    return f"\\frac{{{k}}}{{{m ** 2 - 1}}} x^2 - \\frac{{{n}}}{{{m-1}}}x"

class ProblemKonhauser20216(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=r"Output the answer as a valid LaTex expression in \boxed{...}. Do not include $f(x)$ or dollar signs. For example, \boxed{\frac{3}{4}x + 2}",
        parameters=["n", "k", "m"],
        problem_url="https://drive.google.com/file/d/1yC9Kn09fJY1pwT0Dn4fh-ywhwBv-lXD1/view", # page 5
        solution_url="https://drive.google.com/file/d/1yC9Kn09fJY1pwT0Dn4fh-ywhwBv-lXD1/view", # page 5
        source="Konhauser Problemfest 2021 P6",
        original_parameters={"k": 20, "n": 21, "m": 2},
        original_solution=get_solution(21, 20, 2),
        tags=[Tag.IS_ORIGINAL, Tag.ALGEBRA, Tag.FIND_ANY, Tag.IS_GENERALIZED]
    )
    n: int
    k: int
    m: int

    def __init__(self, n: int, k: int, m: int):
        self.n = n
        self.k = k
        self.m = m

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(n=self.n, k=self.k, m=self.m)

    def check(self, a: str) -> bool:
        if isinstance(a, str) and "=" in a:
            a = a[a.rfind("=") + 1:]
        x = sympy.Symbol("x")
        sympy_expression = latex2sympy_fixed(a)
        try:
            sympy_expression.diff()
        except:
            return False, "The function is not differentiable.", CheckerTag.INCORRECT_SOLUTION
        
        f2x_minus_fx = sympy_expression.subs(x, self.m * x) - sympy_expression
        should_be_0 = f2x_minus_fx - (self.k * x**2 - self.n * x)
        should_be_0 = sympy.simplify(should_be_0)
        if should_be_0 != 0:
            return False, f"The function does not satisfy the condition. The difference is {str(should_be_0)}", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT
        
    @staticmethod
    def generate() -> "ProblemKonhauser20216":
        k = random.randint(1, 50)
        n = random.randint(1, 50)
        m = random.randint(2, 5)
        return ProblemKonhauser20216(n, k, m)
    
    def get_solution(self):
        return get_solution(self.n, self.k, self.m)
