from math_construct.problems.templates import TEMPLATES
PROBLEM_TEMPLATE = TEMPLATES["bmo_shortlist/problem_2019_c1.py"]

from math_construct.problems.problem import Problem, ProblemConfig, Tag, CheckerTag
import random


FORMATTING_INSTRUCTIONS = r"""Output the order as a comma-separated sequence of numbers from 1 to the number of couples, where each number appears exactly twice, inside a \boxed. Consider each 2 duplicate numbers to represent a given couple. For example: \boxed{( 1,2,3,3,1,2)}"""

def get_solution(k: int) -> list[list[int]]:
    res = []
    for i in range(1, 2*k):
        res.append(i//2 + 1)
    return res + [1]

class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n + 1))
        self.rank = [1] * (n + 1)
        self.components = n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # Path compression
        return self.parent[x]

    def union(self, x, y):
        root_x = self.find(x)
        root_y = self.find(y)
        
        if root_x != root_y:
            if self.rank[root_x] > self.rank[root_y]:
                self.parent[root_y] = root_x
            elif self.rank[root_x] < self.rank[root_y]:
                self.parent[root_x] = root_y
            else:
                self.parent[root_y] = root_x
                self.rank[root_x] += 1
            self.components -= 1

def count_connected_components(n, edges):
    uf = UnionFind(2 * n)  # Since we have two partitions of size N
    
    for u, v in edges:
        v += n  # Offset second partition indices
        uf.union(u, v)
    
    unique_roots = set()
    for i in range(1, 2 * n + 1):
        unique_roots.add(uf.find(i))
    
    return len(unique_roots)

class ProblemBMO2019C1(Problem):
    config = ProblemConfig(
        name=Problem.get_name(__file__),
        statement=PROBLEM_TEMPLATE,
        formatting_instructions=FORMATTING_INSTRUCTIONS,
        parameters=["N"],
        source="BMO 2019 Shortlist C1",
        original_parameters={"N": 100},
        original_solution=get_solution(100),
        problem_url="https://artofproblemsolving.com/community/c6h2334522p18764217",
        solution_url="https://artofproblemsolving.com/community/c6h2334522p18764217",
        tags=[Tag.COMBINATORICS, Tag.FIND_ANY, Tag.IS_SIMPLIFIED]
    )
    N: int

    def __init__(self, N: int):
        self.N = N

    def get_problem(self):
        return PROBLEM_TEMPLATE.format(N=self.N, twon=2*self.N, m=self.N-2)

    def check(self, x: tuple[int, list[int]]) -> bool:
        # Note: The checker implements a "smarter" way to check whether the given example works, which boils down to counting the number of components in a bipartite graph
        if len(x) != 2*self.N:
            return False, f"Sequence should be of length {2*self.N}, received {len(x)}", CheckerTag.INCORRECT_LENGTH
        
        counts = {}

        for i in x:
            if i not in counts:
                counts[i] = 0
            counts[i] += 1

        for count in counts:
            if counts[count] != 2:
                return False, f"Each integer should appear exactly twice", CheckerTag.INCORRECT_FORMAT
        connections = []

        for i in range(self.N):
            connections.append((i+1, x[2*i]))
            connections.append((i+1, x[2*i+1]))

        if count_connected_components(self.N, connections) != 1:
            return False, f"You can have everyone dance with their parter in less than {self.N-2} steps", CheckerTag.INCORRECT_SOLUTION

        return True, "OK", CheckerTag.CORRECT

    @staticmethod
    def generate() -> "ProblemBMO2019C1":
        k = random.randint(5, 100)
        return ProblemBMO2019C1(k)

    def get_solution(self):
        return get_solution(self.N)
