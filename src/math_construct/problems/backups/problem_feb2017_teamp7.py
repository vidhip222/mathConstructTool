from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["backups/problem_feb2017_teamp7.py"]

from math_construct.problems.problem import Problem, ProblemConfig, Tag
import numpy as np
import random


EXTRA_FORMATTING_INSTRUCTIONS = r"""Output the answer as a tuple. The first element should contain the answer for {n}. The second should contain a list of indeces $i_0, i_1, \cdots, i_{{p-1}}$, where $i_k = k (\bmod p)$. Output the answer inside of $\boxed{...}$. For example, $\boxed{(3, [1, 2, 0])}$."""


def get_solution(p: int) -> list[int]:
    return (p**2-2, [p-1] + [(p+1)*(i-1) for i in range(1, p)])

class ProblemHMMTFeb2017TeamP7(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=EXTRA_FORMATTING_INSTRUCTIONS,
        parameters=["p"],
        source="HMMT February 2017 Team P7",
        original_parameters={"p": 17},
        original_solution=get_solution(17),
    )
    p: int

    def __init__(self, p: int):
        self.p = p

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(p=self.p)

    def check(self, x: tuple[int, list[int]]) -> tuple[bool, str]:
        
        if not isinstance(x, (list, tuple)) or len(x) != 2:
            return False, "Example should contain 2 entries - 1 for $n$, 1 for the list of indices"

        n, indices = x

        if not isinstance(indices, list) or len(indices) != self.p:
            return False, f"Index list should contain {self.p} numbers"

        if not isinstance(n, int) or n > self.p**2:
            return False, f"Provided $n$ is too large"

        if any(not isinstance(idx, int) or idx < 0 or idx >= n for idx in indices):
            return False, "Invalid index set"

        # Compute Pascal's triangle row modulo p
        prev_row = [1]
        
        for i in range(1, n+1):
            curr_row = [1] * (i + 1)
            for j in range(1, i):
                curr_row[j] = (prev_row[j - 1] + prev_row[j]) % self.p
            prev_row = curr_row  # Swap reference, avoiding unnecessary copies

        for i, idx in enumerate(indices):
            if prev_row[idx] != i:
                return False, f"Example {prev_row[idx]} at index {idx} is not congruent to {i} mod $p$."

        return True
        
    @staticmethod
    def generate() -> "ProblemHMMTFeb2017TeamP7":
        p = random.choice([7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59])
        return ProblemHMMTFeb2017TeamP7(p)

    def get_solution(self):
        return get_solution(self.p)
