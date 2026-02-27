import inspect
from pydantic.dataclasses import dataclass
from pydantic import BaseModel, Field
from typing import Any, Optional, Self, Union
from math_construct.utils import get_problem_name, get_depth
from math_construct.parsing import parse_answer, match_list_depth
from fractions import Fraction
import random
import numpy as np
import time
from loguru import logger
from enum import Enum
import concurrent.futures

class Tag(str, Enum):
    # Categories

    COMBINATORICS = "Combinatorics"
    NUMBER_THEORY = "Number Theory"
    ALGEBRA = "Algebra"
    GEOMETRY = "Geometry"
    PUZZLE = "Puzzle"

    # Type (of the original problem before our edits)

    FIND_ANY = "Find Any" # Find any X that satisfies the condition
    FIND_ALL = "Find All" # Find all X that satisfies the condition (this sometimes works if there are infinitely many and can be described by a class)
    FIND_INF = "Find Infinitely Many" # Find infinitely many X that satisfies the condition
    FIND_MAX_MIN = "Find Max/Min" # Find the maximum or minimum X that satisfies the condition

    # Hardness compared to the original problem

    # is simplified: whether or not the problem is simplified compared to the original
    # e.g. "Find Any" converted "Find N" or "Solve for N" converted to "Solve for N=42"
    IS_SIMPLIFIED = "Is Simplified"
    # is original: whether the "original" problem is actually the exact same as the original
    IS_ORIGINAL = "Is Original"
    # is original: whether the problem statement is actually a more general version of the original
    IS_GENERALIZED = "Is Generalized"

    # Misc tags 
    
    # is translated: whether the problem is a translation of a problem from another language
    IS_TRANSLATED = "Is Translated"

class CheckerTag(str, Enum):
    # length: incorrect number of objects (outermost list size)
    INCORRECT_LENGTH = "Incorrect number of objects"
    # format: more broadly, solution is not in the correct format 
    # (e.g., expected matrix got list, expected 21x21 matrix got 20x20,
    # expected list of 3-tuples but one was a 4-tuple, etc.) 
    INCORRECT_FORMAT = "Incorrect format of the solution"
    # solution: solution is incorrect -- some problem constraint is violated
    INCORRECT_SOLUTION = "Incorrect solution; some constraint violated"
    # unknown: unknown issue (because checker didn't return a CheckerTag)
    UNKNOWN = "Unknown"
    # correct: solution is correct
    CORRECT = "Correct"

@dataclass
class ProblemConfig:
    # A unique identifier for the problem (e.g. "problem-1")
    name: str

    # A problem statement where the parameters are replaced with placeholders (e.g. {a}, {b}, etc.)
    statement: str

    # Instructions for how to format the output (e.g. "Write the answer as a list of integers")
    formatting_instructions: Optional[str]

    # The parameters that are used in the statement (e.g. ["a", "b"])
    parameters: list[str]

    # The source of the problem (e.g. "USAMTS 23/24 Round 1")
    source: str

    original_solution: Any

    original_parameters: Optional[dict[str, str | int | list[str] | list[list[str]]]]

    timeout: int = 60
    
    # The URL of where the problem can be found (e.g. "https://example.com/problem-1")
    problem_url: Optional[str] = None 

    # The URL of where the solution can be found (e.g. "https://example.com/solution-1"), specify only if different from problem_url
    solution_url: Optional[str] = None

    # The original parameters used in the competition (e.g. {"a": 2, "b": 2})

    # The original solution to the problem in the competition (e.g. [["1", "1"], ["1", "1"]])

    tags: list[Tag] = Field(default_factory=list)

class Problem:
    config: ProblemConfig
    solution: Optional[Any] = None

    def __init__(self, config: ProblemConfig, revised_statement: Optional[str] = None, revised_formatting: Optional[str] = None, **kwargs):
        self.config = config
        self.revised_statement = revised_statement
        self.revised_formatting = revised_formatting

    def set_revision(self, revised_statement, revised_formatting):
        self.revised_statement = revised_statement
        self.revised_formatting = revised_formatting

    def set_solution(self, solution):
        self.solution = solution

    def __str__(self):
        if hasattr(self, "revised_statement") and self.revised_statement is not None:
            return self.revised_statement
        else:
            return self.get_problem()
        
    def get_formatting(self):
        if hasattr(self, "revised_formatting") and self.revised_formatting is not None:
            return self.revised_formatting
        else:
            return self.get_formatting_instructions()
    
    @staticmethod
    def check_singular(solution, 
                        is_integer : bool = False, 
                        is_float : bool = False, 
                        min_val_inclusive : float = None, 
                        max_val_inclusive : float = None,
                        min_val_exclusive : float = None,
                        max_val_exclusive : float = None,
            ):
        if is_integer:
            if not isinstance(solution, int):
                return False, f"Expected an integer, got {solution}", CheckerTag.INCORRECT_FORMAT
        if is_float:
            if not isinstance(solution, (float, int)):
                return False, f"Expected a float, got {solution}", CheckerTag.INCORRECT_FORMAT
        if min_val_inclusive is not None and solution < min_val_inclusive:
            return False, f"Expected value to be at least {min_val_inclusive}, got {solution}", CheckerTag.INCORRECT_FORMAT
        if max_val_inclusive is not None and solution > max_val_inclusive:
            return False, f"Expected value to be at most {max_val_inclusive}, got {solution}", CheckerTag.INCORRECT_FORMAT
        if min_val_exclusive is not None and solution <= min_val_exclusive:
            return False, f"Expected value to be more than {min_val_exclusive}, got {solution}", CheckerTag.INCORRECT_FORMAT
        if max_val_exclusive is not None and solution >= max_val_exclusive:
            return False, f"Expected value to be less than {max_val_exclusive}, got {solution}", CheckerTag.INCORRECT_FORMAT
        return True, f"OK", CheckerTag.CORRECT
    
    @staticmethod
    def check_recursive(solution, **kwargs):
        if isinstance(solution, (list, tuple, set)):
            for element in solution:
                is_correct, message, tag = Problem.check_recursive(element, **kwargs)
                if not is_correct:
                    return is_correct, message, tag
            return True, "OK", CheckerTag.CORRECT
        else:
            return Problem.check_singular(solution, **kwargs)
    
    @staticmethod
    def check_format(solution, 
                     expected_length : int = None, 
                     expected_size_all_axes : list[int] = None,
                     is_integer : bool = False, 
                     is_float : bool = False, 
                     is_unique : bool = False, 
                     is_matrix : bool = False, 
                     is_square_matrix : bool = False, 
                     min_val_inclusive : float = None, 
                     max_val_inclusive : float = None,
                     min_val_exclusive : float = None,
                     max_val_exclusive : float = None, 
        ):
        """
        Checks the format of the provided solution based on various criteria.
        Parameters:
            solution (any): The solution to be checked.
            expected_length (int, optional): The expected length of the solution if it is a list or tuple.
            expected_size_all_axes (list[int], optional): The expected size of the solution along each axes. None along an axis is ignored.
            is_integer (bool, optional): Whether the solution should consist of integer values as primitive types.
            is_float (bool, optional): Whether the solution should consist of float values as primitive types.
            is_unique (bool, optional): Whether the solution should contain unique elements if it is a list or tuple.
            is_matrix (bool, optional): Whether the solution should be a matrix (list of lists or tuples).
            is_square_matrix (bool, optional): Whether the solution should be a square matrix.
            min_val_inclusive (float, optional): The minimum inclusive value for elements in the solution, i.e. asserts element >= min_val_inclusive.
            max_val_inclusive (float, optional): The maximum inclusive value for elements in the solution, i.e. asserts element <= max_val_inclusive.
            min_val_exclusive (float, optional): The minimum exclusive value for elements in the solution, i.e. asserts element > min_val_exclusive. 
            max_val_exclusive (float, optional): The maximum exclusive value for elements in the solution, i.e. asserts element < max_val_exclusive.
        Returns:
            tuple: A tuple containing a boolean indicating if the format is correct, a message, and a CheckerTag.
        """
        if expected_length is not None:
            if len(solution) != expected_length:
                return False, f"Expected {expected_length} elements, got {len(solution)}", CheckerTag.INCORRECT_LENGTH
        
        is_correct, message, tag = Problem.check_recursive(solution, is_float=is_float, is_integer=is_integer, 
                                                        min_val_exclusive=min_val_exclusive, min_val_inclusive=min_val_inclusive,
                                                        max_val_exclusive=max_val_exclusive, max_val_inclusive=max_val_inclusive)
        if not is_correct:
            return is_correct, message, tag
        if expected_size_all_axes is not None:
            if not isinstance(solution, (list, tuple)):
                return False, f"Expected a list or tuple, got {solution}", CheckerTag.INCORRECT_FORMAT
            if expected_size_all_axes[0] is not None and len(solution) != expected_size_all_axes[0]:
                return False, f"Expected size {expected_size_all_axes[0]}, got {len(solution)}", CheckerTag.INCORRECT_FORMAT
            if len(expected_size_all_axes) > 1:
                for el in solution:
                    checker = Problem.check_format(el, expected_size_all_axes=expected_size_all_axes[1:])
                    if not checker[0]:
                        return checker

        if is_unique and isinstance(solution, (list, tuple)):
            if not isinstance(solution[0], list) and len(set(solution)) != len(solution):
                return False, f"List contains duplicate elements", CheckerTag.INCORRECT_FORMAT
            else:
                for i, element in enumerate(solution):
                    if element in solution[i+1:]:
                        return False, f"List contains duplicate elements", CheckerTag.INCORRECT_FORMAT
        if is_matrix or is_square_matrix:
            if not isinstance(solution, (list, tuple)):
                return False, f"Expected a matrix, got {solution}", CheckerTag.INCORRECT_FORMAT
            if not all(isinstance(row, (list, tuple)) for row in solution):
                return False, f"Expected a matrix, got {solution}", CheckerTag.INCORRECT_FORMAT
            if not all(len(row) == len(solution[0]) for row in solution):
                return False, f"Matrix is not rectangular", CheckerTag.INCORRECT_FORMAT
        if is_square_matrix:
            if not all(len(row) == len(solution) for row in solution):
                return False, f"Matrix is not square", CheckerTag.INCORRECT_FORMAT
        return True, "OK", CheckerTag.CORRECT
        
    def check_with_timeout(self, answer):
        """
        Runs the check function with a timeout.
        """
        with concurrent.futures.ProcessPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.check, answer)
            try:
                result = future.result(timeout=self.config.timeout)
                return result
            except concurrent.futures.TimeoutError:
                future.cancel()
                raise TimeoutError(f"check() did not complete within {self.config.timeout} seconds.")

    # Always returns answer, is_correct, details
    def parse_and_check(self, output_str: Union[list[dict[str]], str]) -> tuple[str, bool, str]:
        self.warn_small_length(output_str)
        try:
            logger.trace(f"Parsing solution: {output_str}")
            answer = self.parse(output_str)
            logger.trace(f"Parsed solution: {answer}")
        except Exception as e:
            err = f"Error parsing solution: {e}"
            logger.warning(err)
            return None, False, err
        if answer is None:
            return None, False, "Parser returned None"
        try:
            checker_result = self.check_with_timeout(answer)
            if type(checker_result) == tuple and len(checker_result) == 3:
                is_correct, details, error_tag = checker_result
            elif type(checker_result) == bool:
                logger.error(f"Checker did not return a tag. Returning as unknown.")
                is_correct = checker_result 
                details = '(!) Checker did not return details.'
                error_tag = CheckerTag.UNKNOWN 
            elif type(checker_result) == tuple and len(checker_result) == 2:
                logger.error(f"Checker did not return a tag. Returning as unknown.")
                is_correct, details = checker_result
                error_tag = CheckerTag.UNKNOWN
            else:
                raise TypeError(f"Unexpected checker return value: {checker_result}")
            return answer, is_correct,  f"{error_tag}: {details}"
        except Exception as e:
            err = f"Error checking solution: {e}"
            logger.warning(err)
            return answer, False, err 

    # below should be private vvv
    @classmethod
    def parse_list(cls, output: list[dict[str]]):
        parsed_response = None
        caught_error = None
        for i, s in enumerate(output[::-1]):
            if isinstance(s, str):
                try:
                    parsed_response = cls.parse(s)
                except Exception as e:
                    if r"Final solution needs to be encased in \boxed{}." in str(e) and caught_error is not None:
                        continue
                    caught_error = e
                if parsed_response is not None:
                    caught_error = None
                    break
            elif s["role"] == "assistant" or "```" in s["content"]: # code output or assistant message
                try:
                    parsed_response = cls.parse(s["content"])
                except Exception as e:
                    if r"Final solution needs to be encased in \boxed{}." in str(e) and caught_error is not None:
                        continue
                    caught_error = e
                if parsed_response is not None:
                    caught_error = None
                    break
        if caught_error is not None:
            raise caught_error
        return parsed_response
    
    @classmethod
    def warn_small_length(cls, query):
        total_length = 0
        for message in query:
            if message["role"] == "assistant":
                if message["content"] is None:
                    logger.error(f"Assistant message is None. For sure something went wrong")
                    return
                total_length += len(message["content"])
        if total_length == 0:
            logger.warning(f"Model did not give output. This might indicate that something went wrong (except for o1).")

    @classmethod
    def parse(cls, output_str: Union[list[dict[str]], str]):
        if isinstance(output_str, list):
            return cls.parse_list(output_str)
        if len(output_str) == 0: # reasoning model didn't finish -> don't allow it to restart from scratch by throwing an error (costs a lot)
            return None
        match = cls.extract_last_boxed_content(output_str)
        if match is None:
            raise Exception(r"No \boxed content found in solution. Final solution needs to be encased in \boxed{}.")
        primitive_type, depth = cls.get_primitive_type(), get_depth(cls.config.original_solution)
        res = parse_answer(match, primitive_type)
        if res is None:
            raise Exception(f"Could not parse the solution from extracted boxed answer: {match}.")
        try:
            res = match_list_depth(res, depth, primitive_type)
        except Exception as e:
            err = f"Could not match the list depth of expected answer: {e}. Raw solution was {match}."
            raise Exception(err) # re-raise
        return res

    @staticmethod
    def extract_last_boxed_content(text):
        """
        Return the content of the last \boxed{...} found in 'text'.
        Returns None if no matching pair is found.
        """
        start_index = text.rfind(r'\boxed{')
        if start_index == -1:
            # "\boxed{" not found at all
            return None
        brace_start_index = start_index + len(r'\boxed{')
        open_braces = 1
        i = brace_start_index

        while i < len(text) and open_braces > 0:
            if text[i] == '{':
                open_braces += 1
            elif text[i] == '}':
                open_braces -= 1
            i += 1
        if open_braces != 0:
            return None
        return text[brace_start_index : i - 1]

    
    @classmethod
    def get_primitive_type(cls, solution = None):
        if solution is None:
            solution = cls.config.original_solution
        if isinstance(solution, (list, tuple, set)):
            all_types = [cls.get_primitive_type(sol) for sol in solution]
            if any([t is None for t in all_types]):
                return None
            # if consists of all floats and ints, return float
            if len(set(all_types)) == 1:
                return all_types[0]
            if all([t in (int, float) for t in all_types]):
                return float
            if len(set(all_types)) > 1:
                return None
            return all_types[0]
        return type(solution)
    
    def get_problem(self):
        return self.config.statement.format(**self.to_json()["param_values"])

    def get_formatting_instructions(self):
        return self.config.formatting_instructions

    def check(self, solution: list[str | int | float]) -> Union[bool, tuple[bool, str, CheckerTag]]:
        """Check if the solution is correct"""
        raise NotImplementedError("You must implement this method for each problem")

    # For tests that do not care about details nor issue tags
    def check_raw(self, solution: list[str | int | float]) -> bool: 
        checker_result = self.check(solution)
        if type(checker_result) == tuple:
            return checker_result[0]
        else:
            return checker_result

    @classmethod
    def get_original(cls) -> "Problem":
        """Get the original problem"""
        return cls(**cls.config.original_parameters)

    def is_original(self) -> bool:
        param_values = {
            param: getattr(self, param)
            for param in self.config.parameters
        }
        orig_param_values = self.config.original_parameters
        if len(param_values) != len(orig_param_values):
            return False
        for k, v in param_values.items():
            if k not in orig_param_values or orig_param_values[k] != v:
                return False
        return True

    @staticmethod
    def generate() -> "Problem":
        """Generate a new instance of the problem"""
        raise NotImplementedError("You must implement this method for each problem")
    
    @classmethod
    def generate_with_seed(cls, seed: int) -> "Problem":
        random.seed(seed)
        np.random.seed(seed)
        return cls.generate()
    
    @classmethod
    def generate_multiple_explicit(cls, n_problems: int = None) -> list["Problem"]:
        if n_problems is None:
            n_problems = 1
        return cls.generate_multiple(n_problems)
    
    @classmethod
    def generate_multiple(cls, n_problems: int, n_tries: int = 1000, seed_start: int = 0, 
                          include_original: bool = True) -> list["Problem"]:
        """Generate n_problems unique problems"""
        problems = []
        if include_original:
            problems.append(cls.get_original())
        if n_problems == 1:
            return problems
        for j in range(n_tries):
            problem = cls.generate_with_seed(seed_start + j)
            if all(problem != p for p in problems):
                problems.append(problem)

            if len(problems) == n_problems:
                break
        return problems
    
    def __eq__(self, other):
        if not isinstance(other, Problem):
            return False
        return self.to_json() == other.to_json()

    def __ne__(self, value):
        return not self.__eq__(value)

    @classmethod
    def generate_instances(cls, n: int) -> list["Problem"]:
        """Generate n unique instances of the problem"""
        problems = []
        found_param_values = set()
        for _ in range(n):
            new_problem = None
            for _ in range(100):
                candidate_problem = cls.generate()
                param_values = {
                    param: getattr(candidate_problem, param)
                    for param in candidate_problem.config.parameters
                }
                hash_param_values = hash(frozenset(param_values.items()))
                if hash_param_values not in found_param_values:
                    found_param_values.add(hash_param_values)
                    new_problem = candidate_problem
                    break
            if new_problem is None:
                raise ValueError("Could not generate unique problem instances")
            problems.append(new_problem)
        return problems

    @classmethod
    def has_variations(cls) -> bool:
        """Return True if the problem has variations different from the original problem."""
        return True
    
    def remove_fractions_from_json(self, param_value):
        if isinstance(param_value, Fraction):
            return float(param_value)
        if isinstance(param_value, dict):
            return {k: self.remove_fractions_from_json(v) for k, v in param_value.items()}
        if isinstance(param_value, (list, tuple)):
            return [self.remove_fractions_from_json(v) for v in param_value]
        return param_value

    def to_json(self) -> dict:
        """Convert the problem instance to a JSON-serializable dictionary"""
        param_values = {
            param: getattr(self, param)
            for param in self.config.parameters
        }
        dict_config = self.remove_fractions_from_json(self.config.__dict__)
        revised_statement = self.revised_statement if hasattr(self, "revised_statement") else None
        revised_formatting = self.revised_formatting if hasattr(self, "revised_formatting") else None
        return {
            "config": dict_config,
            "param_values": param_values,
            "revised_statement": revised_statement,
            "revised_formatting": revised_formatting
        }

    @classmethod
    def from_json(cls, data: dict) -> Self:
        """Create a problem instance from a JSON-serializable dictionary"""
        obj = cls(**data["param_values"])
        if "revised_statement" in data and "revised_formatting" in data:
            obj.set_revision(data["revised_statement"], data["revised_formatting"])
        return obj

    @classmethod
    def get_name(cls, file_path: Optional[str] = None) -> str:
        """Get the problem name"""
        if file_path is not None:
            return get_problem_name(file_path)
        return get_problem_name(inspect.getfile(cls))

    def get_solution(self):
        if self.solution is not None:
            return self.solution
        return None
