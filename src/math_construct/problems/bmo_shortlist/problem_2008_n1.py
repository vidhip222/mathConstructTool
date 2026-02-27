from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["bmo_shortlist/problem_2008_n1.py"]

from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
from math_construct.templates import INTEGER_FORMATTING_TEMPLATE
import sys
sys.set_int_max_str_digits(1000000)
import numpy as np
import random


def euler_totient(n):
    """
    Calculate the Euler's Totient function φ(n), which counts the integers
    between 1 and n inclusive that are coprime with n.
    
    Args:
        n (int): The input number.
        
    Returns:
        int: The value of φ(n).
    """
    if n == 0:
        return 0
    if n == 1:
        return 1

    result = n
    p = 2  # Start checking from the first prime
    
    while p * p <= n:
        # Check if p is a prime factor of n
        if n % p == 0:
            # If p divides n, subtract multiples of p
            while n % p == 0:
                n //= p
            result -= result // p
        p += 1

    # If n has a prime factor greater than sqrt(n), subtract its contribution
    if n > 1:
        result -= result // n
    
    return result

def get_solution(a: int) -> list[int]:
    x = a*10**len(str(a)) - 1
    k = 0
    b = 1
    t = 1
    while k < len(str(b)):
        k = t*euler_totient(x) - len(str(a))
        t+=1
        if (a*10**k-a**2) % x != 0:
            continue
        
        b = (a*10**k-a**2) // x

    return a*10**k + b

class ProblemBMO2008N1(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=INTEGER_FORMATTING_TEMPLATE,
        parameters=["a"],
        source="BMO 2008 Shortlist N1",
        original_parameters={"a": 12},
        original_solution=get_solution(12),
        problem_url="https://artofproblemsolving.com/community/c6h2053042p14598681",
        solution_url="https://artofproblemsolving.com/community/c6h2053042p14598681",
        tags=[Tag.NUMBER_THEORY, Tag.FIND_ANY, Tag.IS_SIMPLIFIED]
    )
    m: int
    n: int

    def __init__(self, a: int):
        self.a = a

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(a = self.a)

    def check(self, x: int) -> bool:
        if not str(x).startswith(str(self.a)):
            return False, f'Answer {x} does not begin with {self.a}', CheckerTag.INCORRECT_FORMAT
        if len(str(x)) == len(str(self.a)):
            return False, f'Answer {x} does not have enough digits', CheckerTag.INCORRECT_FORMAT
        rest = int(str(x)[len(str(self.a)):])
        new = self.a*(rest*10**len(str(self.a)) + self.a)

        if x != new:
            return False, 'Property not satisfied', CheckerTag.INCORRECT_SOLUTION      
            
        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "ProblemBMO2008N1":
        a = random.randint(6, 20)
        return ProblemBMO2008N1(a)

    def get_solution(self):
        return get_solution(self.a)
