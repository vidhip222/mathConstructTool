from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["imc/problem_2013_3.py"]

import random
import numpy as np
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag 
from math_construct.templates import get_matrix_template


def get_solution(n: int):
    trips = []
    def organize_trip(subsets: list[list[int]]):
        res = [0]*(2*n)
        for sub in subsets:
            for id in sub:
                res[id] = 1
        trips.append(res)
    def divide(a, b, k):
        assert (b-a)%k == 0
        return [[a+j*(b-a)//k+i for i in range((b-a)//k)] for j in range(k)]
    
    if n%2 == 0:
        A, B, C, D = divide(0, 2*n, 4)
        organize_trip([A, B])
        organize_trip([C, D])
        organize_trip([A, C])
        organize_trip([B, D])
        organize_trip([A, D])
        organize_trip([B, C])
    elif n%2 == 1 and n%3 == 0:
        E, F, G, H, I, J = divide(0, 2*n, 6)
        organize_trip([E, F, G])
        organize_trip([E, F, H])
        organize_trip([G, H, I])
        organize_trip([G, H, J])
        organize_trip([E, I, J])
        organize_trip([F, I, J])
    else:
        y = n//3
        if (n-3*y) % 2 != 0:
            y -= 1
        x = (n-3*y)//2
        assert n == 2*x+3*y and x >= 1 and y >= 1
        A, B, C, D = divide(0, 4*x, 4)
        E, F, G, H, I, J = divide(4*x, 2*n, 6)
        organize_trip([A, B, E, F, G])
        organize_trip([C, D, E, F, H])
        organize_trip([A, C, G, H, I])
        organize_trip([B, D, G, H, J])
        organize_trip([A, D, E, I, J])
        organize_trip([B, C, F, I, J])
    return trips


class Problem_IMC_2013_3(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_matrix_template(),
        parameters=["n"],
        source="IMC 2013 P3",
        original_parameters={"n": 10},
        original_solution=get_solution(10),
        problem_url="https://www.imc-math.org.uk/imc2013/IMC2013-day1-solutions.pdf",
        solution_url="https://www.imc-math.org.uk/imc2013/IMC2013-day1-solutions.pdf",
        tags=[Tag.COMBINATORICS, Tag.FIND_MAX_MIN, Tag.IS_SIMPLIFIED],
    )
    n: int

    def __init__(self, n: int):
        self.n = n

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(n=self.n)

    def check(self, x: list[list[int]]):
        if len(x) != 6:
            return False, f"There should be 6 trips.", CheckerTag.INCORRECT_LENGTH
        for trip in x:
            if len(trip) != 2*self.n:
                return False, f"The number of columns is not equal to 2n ({2*self.n}).", CheckerTag.INCORRECT_LENGTH
            if not all(x == 0 or x == 1 for x in trip):
                return False, f"Some elements are not 0 or 1.", CheckerTag.INCORRECT_FORMAT
            if sum(trip) != self.n:
                return False, f"Trip does not have exactly n students ({self.n}).", CheckerTag.INCORRECT_SOLUTION
        for i in range(2*self.n):
            for j in range(i+1, 2*self.n):
                cnt = 0
                for trip in x:
                    if trip[i] == 1 and trip[j] == 1:
                        cnt += 1
                if cnt == 0:
                    return False, f"Students {i} and {j} are never together on any trip.", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT
        
    @classmethod
    def generate_multiple_explicit(cls, n_problems: int = None) -> list["Problem"]:
        # not used in avg plot
        small = np.linspace(2, 8, 5).astype(int).tolist()
        mid = np.linspace(9, 20, 10).astype(int).tolist()
        big = np.linspace(21, 180, 9).astype(int).tolist() 
        return [cls(n) for n in small + mid + big]

    @staticmethod
    def generate() -> "Problem_IMC_2013_3":
        n = random.randint(8, 20)
        return Problem_IMC_2013_3(n)

    def get_solution(self):
        return get_solution(self.n)
