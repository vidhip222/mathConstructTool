from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["usamts/problem_1998_4_1.py"]

import random
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_integer_template


def get_solution(a: int, b: int, n: int) -> str:
    if n == 1:
        return str(a)
    x = get_solution(a, b, n - 1)
    if int(x) % (2 ** n) == 0:
        return str(a) + x
    return str(b) + x

class Problem3(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_integer_template(),
        parameters=["a", "b", "n"],
        source="USAMTS 98/99 Round 4",
        original_parameters={"a": 8, "b": 9, "n": 31},
        original_solution=get_solution(8, 9, 31),
        problem_url="https://files.usamts.org/Problems_10_4.pdf",
        solution_url="https://files.usamts.org/Solutions_10_4.pdf",
        tags=[Tag.NUMBER_THEORY, Tag.IS_ORIGINAL, Tag.IS_GENERALIZED, Tag.FIND_ANY]
    )
    a: int
    b: int
    n: int

    def __init__(self, a: int, b: int, n: int):
        assert a % 2 == 0 and 0 <= a and a <= 9
        assert b % 2 == 1 and 0 <= b and b <= 9
        self.a = a
        self.b = b
        self.n = n

    def check(self, x: str):
        if len(x) != self.n:
            return False, f"List of size {len(x)}, should be {self.n}", CheckerTag.INCORRECT_LENGTH
        if not isinstance(x, str):
            return False, "Solution should be a string", CheckerTag.INCORRECT_FORMAT
        if not all(c in [str(self.a), str(self.b)] for c in x):
            return False, f"Not all digits are {self.a} or {self.b}", CheckerTag.INCORRECT_SOLUTION
        if int(x) % (2 ** self.n) != 0:
            return False, f"{x} is not a multiple of {2 ** self.n}", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "Problem3":
        a = 2 * random.randint(1, 4)
        b = 2 * random.randint(1, 4) + 1
        n = random.randint(25, 50)
        return Problem3(a, b, n)

    def get_solution(self) -> str:
        return get_solution(self.a, self.b, self.n)

        
