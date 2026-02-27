from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["backups/problem_2022_12_selection.py"]

import sympy
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.utils import latex2sympy_fixed


class ProblemSwissSelection202212(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=r"Write a valid LaTeX function in function of the variable $x$ that does not contain $f(x)$ inside \boxed. For instance, \boxed{x^2} or \boxed{e^x}.",
        parameters=[],
        problem_url="https://mathematical.olympiad.ch/fileadmin/user_upload/Archiv/Intranet/Olympiads/Mathematics/deploy/exams/2022/Selection/MasterSolution/selectionSolution2022.pdf#page=25",
        solution_url="https://mathematical.olympiad.ch/fileadmin/user_upload/Archiv/Intranet/Olympiads/Mathematics/deploy/exams/2022/Selection/MasterSolution/selectionSolution2022.pdf#page=25",
        source="Swiss Math Olympiad IMO Selection 2022",
        original_parameters=dict(),
        original_solution=r"\frac{1}{x}",
        tags=[Tag.IS_ORIGINAL, Tag.FIND_ANY, Tag.ALGEBRA, Tag.IS_SIMPLIFIED]
    )

    def __init__(self):
        pass

    def get_problem(self):
        return PROBLEM_TEMPLATE
        
    def check(self, a: str) -> bool:
        if isinstance(a, str) and "=" in a:
            a = a[a.rfind("=") + 1:]
        sympy_expression = latex2sympy_fixed(a)
        if sympy_expression is None:
            return False, "Invalid LaTeX expression.", CheckerTag.INCORRECT_FORMAT
        x = sympy.symbols("x")
        f_x_times_x = x * sympy_expression # simple automatic check if this is constant
        simplified = sympy.simplify(f_x_times_x)
        if simplified != 1:
            return False, "Function does not satisfy the inequality.", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @classmethod
    def has_variations(cls):
        return False

    @staticmethod
    def generate() -> "ProblemSwissSelection202212":
        return ProblemSwissSelection202212()
    
    def get_solution(self):
        return r"\frac{1}{x}"
