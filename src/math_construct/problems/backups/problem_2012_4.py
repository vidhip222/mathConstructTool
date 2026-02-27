from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["backups/problem_2012_4.py"]

import random
from sympy.ntheory import divisors
from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.utils import get_latex_array
from math_construct.templates import get_integer_template


# Brute force by Claude
def check_number(n, d):
    if n % d != 0:
        return False
    
    # Convert number to string
    num_str = str(n)
    
    # Try removing each digit
    for i in range(len(num_str)):
        if num_str[i] == '0':  # Skip zero digits
            continue
            
        new_num_str = num_str[:i] + num_str[i+1:]
        new_num = int(new_num_str)
        if new_num % d == 0:
            return True
    return False

def brute_force(d: int):
    for i in range(1, 1000000):
        n = i * d
        if check_number(n, d):
            return n
    return None

def get_solution(d: int):
    b = 1
    while (d - b) % 9 != 0:
        b += 1
    a = (d - b) // 9
    k = 1
    while 10**(k-1) <= d:
        k += 1
    x = a*10**k + 10**(k-1)
    q, r = divmod(x, d)
    c = 10**(k-1)-r
    return 10**k * (10*a + b) + c

class Problem_HMO_2012_4(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=get_integer_template(),
        parameters=["d"],
        source="HMO 2012 Memo Test Problem 4",
        original_parameters={"d": 1046},
        original_solution=get_solution(1046),
        tags=[Tag.NUMBER_THEORY, Tag.FIND_ANY, Tag.IS_TRANSLATED, Tag.IS_SIMPLIFIED],
        problem_url="https://natjecanja.math.hr/wp-content/uploads/2015/02/2012_izborno-rjesenja.pdf#page=20", # page 20
        solution_url="https://natjecanja.math.hr/wp-content/uploads/2015/02/2012_izborno-rjesenja.pdf#page=20", # page 20
    )
    d: int

    def __init__(self, d: int):
        self.d = d

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(d=self.d)

    def check(self, n: int):
        if n % self.d != 0:
            return False, f"{n} is not divisible by {self.d}", CheckerTag.INCORRECT_SOLUTION
        s = str(n)
        for i in range(len(s)):
            if s[i] != "0":
                new_s = s[:i] + s[i+1:]
                if int(new_s) % self.d == 0:
                    return True, "OK", CheckerTag.CORRECT
        return False, "No digit can be deleted to make the number divisible by d", CheckerTag.INCORRECT_SOLUTION

    @staticmethod
    def generate() -> "Problem_HMO_2012_4":
        d = random.randint(1000, 1000000)
        while brute_force(d) is not None:
            d = random.randint(1000, 1000000)
        return Problem_HMO_2012_4(d)

    def get_solution(self):
        return get_solution(self.d)
