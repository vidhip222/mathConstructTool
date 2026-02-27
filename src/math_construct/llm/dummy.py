from math_construct.problems.problem import Problem

PROMPT = """{system_prompt}

Please use the following format for your response:
{format_instructions}

Problem:
{problem}
"""

class DummyLLM:

    def __init__(self, fixed_response):
        self.fixed_response = fixed_response
        

    def generate_solution(self, problem: Problem, **kwargs) -> str:
        prompt = PROMPT.format(
            system_prompt="This is a dummy LLM that always returns the same response.",
            format_instructions=problem.config.formatting_instructions,
            problem=str(problem)
        )

        response = f"{prompt}\n\nThe answer is: {self.fixed_response}"
        return response
