from .. import APIQuery

class Solver:
    def __init__(self, querier: APIQuery):
        self.querier = querier
        self.cost = 0
        self.detailed_cost = []
    
    def solve(self, problems):
        raise NotImplementedError