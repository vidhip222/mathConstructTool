from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["backups/problem_2016_6.py"]

import random
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import get_list_template


def get_solution(k):
    return [i for i in range(1, 4 * k + 1, 2)]

class ProblemKonhauser20166(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_list_template(r"The $i$-the element in the list should be $a_i$."),
        parameters=["k"],
        source="Konhauser Problemfest 2016",
        problem_url="https://www.macalester.edu/mscs/wp-content/uploads/sites/591/2016/03/Konhauser2016.pdf#page=3",
        solution_url="https://www.macalester.edu/mscs/wp-content/uploads/sites/591/2016/03/Konhauser2016.pdf#page=10",
        original_parameters={"k": 10},
        original_solution=get_solution(10),
        tags=[Tag.IS_SIMPLIFIED, Tag.ALGEBRA, Tag.FIND_ANY] 
    )
    k: int

    def __init__(self, k: int):
        self.k = k

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(k=self.k)

    def check(self, sol: list[int]) -> bool:
        checker_format = self.check_format(sol, expected_length=2 * self.k, min_val_exclusive=0)
        if not checker_format[0]:
            return checker_format
        bs = []
        # check that a is strictly increasing and arithmetic
        diffs = [sol[i+1] - sol[i] for i in range(len(sol) - 1)]

        if diffs[0] <= 0:
            return False, "The sequence is not strictly increasing.", CheckerTag.INCORRECT_SOLUTION
        
        if any([abs(diffs[i] - diffs[i+1]) > 1e-6 for i in range(len(diffs) - 1)]):
            return False, "The sequence is not arithmetic.", CheckerTag.INCORRECT_SOLUTION
        
        for i in range(self.k):
            b_i = sum(sol[:i+1]) / sum(sol[i+1:2*i+2])
            bs.append(round(b_i, 6))
        if len(set(bs)) != 1:
            return False, f"The sequence is not constant, {bs}", CheckerTag.INCORRECT_SOLUTION
        return True, "OK", CheckerTag.CORRECT
        
    @staticmethod
    def generate() -> "ProblemKonhauser20166":
        k = random.randint(5,50)
        return ProblemKonhauser20166(k)
    
    def get_solution(self):
        return get_solution(self.k)
