from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["konhauser/problem_2013_1.py"]

import math
import random
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag


LIST_FORMATTING_TEMPLATE = r"""Output the answer as a comma separated list of lists inside of $\boxed{...}$. For example $\boxed{(1,1), (1,\sqrt{2})}$."""



def get_solution(a, b):
    x = min(a, b)
    y = math.sqrt(a**2 + b**2)
    circumference = a + b + y
    D = math.sqrt(circumference**2 - 8 * x * y)
    p = (D + circumference) / 4
    q = (circumference - D) / 4
    Q = (0, x - q) if b == x else (x - q, 0)
    P = (a * p / y, x - p * b / y) if b == x else (x - p * a / y, p * b / y)
    return [list(Q), list(P)]


class ProblemKonhauser20131(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=LIST_FORMATTING_TEMPLATE,
        problem_url="https://www.macalester.edu/mscs/wp-content/uploads/sites/591/2015/01/KP2013.pdf#page=1",
        solution_url="https://www.macalester.edu/mscs/wp-content/uploads/sites/591/2015/01/KP2013.pdf#page=3",
        parameters=["a", "b"],
        source="Konhauser Problemfest 2015 P1",
        original_parameters={"a": 4, "b": 3},
        original_solution=get_solution(4, 3),
        tags=[Tag.GEOMETRY, Tag.IS_ORIGINAL, Tag.IS_GENERALIZED, Tag.FIND_ANY]
    )
    a: int
    b: int

    def __init__(self, a: int, b: int):
        self.a = a
        self.b = b

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(
            a=self.a, b=self.b
        )
    
    def triangle_area(self, p1, p2, p3):
        (x1, y1), (x2, y2), (x3, y3) = p1, p2, p3
        return abs(x1*(y2 - y3) + x2*(y3 - y1) + x3*(y1 - y2)) / 2
    
    def check_on_line(self, p1, p2, p3):
        # check if p1 is on the line p2p3
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        if not abs((x1 - x2) * (y3 - y2) - (y1 - y2) * (x3 - x2)) < 0.0001:
            return False
        # p1 needs to be between p2 and p3
        if x2 != x3:
            return min(x2, x3) <= x1 <= max(x2, x3)
        return min(y2, y3) <= y1 <= max(y2, y3)
    
    def distance(self, p1, p2):
        x1, y1 = p1
        x2, y2 = p2
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def check(self, sol: list[list[float]]) -> bool:
        checker_format = self.check_format(sol, is_square_matrix=True, expected_length=2)
        if not checker_format[0]:
            return checker_format
        A = (self.a, 0)
        B = (0, self.b)
        C = (0, 0)
        P, Q = tuple(sol[0]), tuple(sol[1])
        all_line_checks = [
            [self.check_on_line(P, A, B), self.check_on_line(Q, A, B)],
            [self.check_on_line(P, B, C), self.check_on_line(Q, B, C)],
            [self.check_on_line(P, A, C), self.check_on_line(Q, A, C)],
        ]
        if all([not x[0] for x in all_line_checks]):
            return False, f"P should be on the triangle.", CheckerTag.INCORRECT_SOLUTION
        if all([not x[1] for x in all_line_checks]):
            return False, f"Q should be on the triangle.", CheckerTag.INCORRECT_SOLUTION
        point_in_between = C if not any(all_line_checks[0]) else A if not any(all_line_checks[1]) else B
        area = self.triangle_area(A, B, C)
        area_PQBetween = self.triangle_area(P, point_in_between, Q)
        if abs(area_PQBetween - area / 2) > 0.0001:
            return False, f"The area of PQ should be half the area of the triangle, but area is {area} and area of small triangle is {area_PQBetween}.", CheckerTag.INCORRECT_SOLUTION
        perimeter = self.distance(A, B) + self.distance(B, C) + self.distance(A, C)
        half_perimeter = self.distance(P, point_in_between) + self.distance(Q, point_in_between)
        if abs(half_perimeter - perimeter / 2) > 0.0001:
            return False, f"The perimeter of PQ should be half the perimeter of the triangle, but perimeter is {perimeter} and perimeter of PQ is {half_perimeter}.", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT
        
    @staticmethod
    def generate() -> "ProblemKonhauser20131":
        pythagorean_triples = [
            (m**2 - n**2, 2 * m * n, m**2 + n**2) for m in range(1, 10) for n in range(1, m)
        ]
        perimeters = [sum(x) for x in pythagorean_triples]
        valid_triples = []
        for triple, perimeter in zip(pythagorean_triples, perimeters):
            if perimeter ** 2 < 2 * min(triple) * max(triple):
                continue
            if (perimeter + math.sqrt(perimeter ** 2 - 2 * min(triple) * max(triple))) % 2 < max(triple):
                valid_triples.append(triple)
        a, b, _ = random.choice(valid_triples)
        return ProblemKonhauser20131(a=a, b=b)

    def get_solution(self):
        return get_solution(self.a, self.b)
