from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["swiss/problem_2024_12_selection.py"]

import sympy
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.utils import latex2sympy_fixed


class ProblemSwissSelection202412(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=r"Write a valid LaTeX function as a function of the variable $n$ that does not contain $f(n)$, inside \boxed. For instance, \boxed{n^2} or \boxed{e^n}.",
        problem_url="https://mathematical.olympiad.ch/fileadmin/user_upload/Archiv/Intranet/Olympiads/Mathematics/deploy/exams/2024/Selection/MasterSolution/selectionSolution2024.pdf#page=36",
        solution_url="https://mathematical.olympiad.ch/fileadmin/user_upload/Archiv/Intranet/Olympiads/Mathematics/deploy/exams/2024/Selection/MasterSolution/selectionSolution2024.pdf#page=36",
        parameters=[],
        source="Swiss Math Olympiad IMO Selection 2024",
        original_parameters=dict(),
        original_solution="n+1",
        tags=[Tag.IS_ORIGINAL, Tag.FIND_ALL, Tag.ALGEBRA, Tag.IS_SIMPLIFIED]
    )

    def __init__(self):
        pass

    def get_problem(self):
        return PROBLEM_TEMPLATE
        
    def check(self, a: str) -> bool:
        if "=" in a:
            a = a[a.rfind("=") + 1:]
        sympy_expression = latex2sympy_fixed(a)
        if sympy_expression is None:
            return False, "Invalid LaTeX expression.", CheckerTag.INCORRECT_FORMAT
        n = sympy.symbols("n")
        diff = sympy.simplify(sympy_expression - (n + 1))
        if diff != 0:
            return False, f"Expected {n+1}, got {sympy_expression}.", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "ProblemSwissSelection202412":
        return ProblemSwissSelection202412()
    
    def get_solution(self):
        return "n+1"
    
    @classmethod
    def has_variations(cls):
        return False
