import pytest
from math_construct.problems.usamts.problem_1998_4_1 import Problem3
from math_construct.problems.usamts.problem_2001_4_4 import Problem10
from math_construct.problems import Problem
from math_construct.utils import get_depth
import time
from fractions import Fraction

def test_primitive_and_depth():
    assert Problem3.get_primitive_type(1) == int
    assert Problem3.get_primitive_type([1, [2, 3], [[4, 5, 6]]]) == int
    assert Problem3.get_primitive_type([1, [2, "3"], [[4, 5, 6]]]) is None
    assert Problem3.get_primitive_type([["2", "1"], ["1"]]) == str
    assert Problem3.get_primitive_type([[Fraction(1,2)], [Fraction(1,2)]]) == Fraction
    assert get_depth(1) == 0
    assert get_depth([1, [2, 3], [[4, 5, 6]]]) == None
    assert get_depth([[1, 2], [3, 4]]) == 2
    assert get_depth([[[1, 2], [3, 4]]]) == 3

def pickle_x(x):
    time.sleep(4)

def test_timeout_checker():
    problem = Problem3(8, 9, 13)
    problem.config.timeout = 2
    problem.check = pickle_x
    with pytest.raises(TimeoutError):
        problem.check_with_timeout("123")

def test_check_format():
    assert Problem.check_format([1, 2, 3], is_integer=True)[0]
    assert not Problem.check_format([1.001, 2, 3], is_integer=True)[0]
    assert Problem.check_format([[1, 2, 3], [4,5,6]], is_integer=True)[0]
    assert Problem.check_format([1, 2, 3], is_float=True)[0]
    assert not Problem.check_format([1, 2, "s"], is_float=True)[0]
    assert Problem.check_format([1, 2, 2.5], is_float=True)[0]
    assert Problem.check_format([1,2,3], expected_length=3)[0]
    assert not Problem.check_format([1,2,3], expected_length=4)[0]
    assert Problem.check_format([[1,2,3], [4,5,6]], expected_length=2)[0]
    assert Problem.check_format([1,2,3], is_unique=True)[0]
    assert not Problem.check_format([1,2,2], is_unique=True)[0]
    assert not Problem.check_format([[1,2,3], [4,5,6], [1,2,3]], is_unique=True)[0]
    assert Problem.check_format([[1,2,3], [4,5,6], [7,8,9]], is_unique=True)[0]
    assert Problem.check_format([[1,2,3], [4,5,6], [7,8,9]], is_matrix=True)[0]
    assert Problem.check_format([[1,2,3], [4,5,6], [7,8,9]], is_square_matrix=True)[0]
    assert not Problem.check_format([[1,2,3], [4,5,6], [7,8,9], [10, 11, 12]], is_square_matrix=True)[0]
    assert Problem.check_format([[1,2,3], [4,5,6], [7,8,9], [10, 11, 12]], is_matrix=True)[0]
    assert not Problem.check_format([[1,2], [4,5,6], [7,8,9], [10, 11, 12]], is_matrix=True)[0]
    assert Problem.check_format([[1,2], [4,5], [7,8]], min_val_exclusive=0)[0]
    assert not Problem.check_format([[1,2], [4,5], [7,8]], min_val_exclusive=1)[0]
    assert Problem.check_format([[1,2], [4,5], [7,8]], max_val_exclusive=9)[0]
    assert not Problem.check_format([[1,2], [4,5], [7,8]], max_val_exclusive=8)[0]
    assert Problem.check_format([[1,2], [4,5], [7,8]], min_val_inclusive=1)[0]
    assert not Problem.check_format([[1,2], [4,5], [7,8]], min_val_inclusive=2)[0]
    assert Problem.check_format([[1,2], [4,5], [7,8]], max_val_inclusive=8)[0]
    assert not Problem.check_format([[1,2], [4,5], [7,8]], max_val_inclusive=7)[0]

    assert Problem.check_format([1, 2, 3], expected_size_all_axes=[3])[0]
    assert Problem.check_format([[1, 2], [3, 4]], expected_size_all_axes=[2, 2])[0]
    assert Problem.check_format([[[1, 2], [3, 4]], [[5, 6], [7, 8]]], expected_size_all_axes=[2, 2, 2])[0]
    assert Problem.check_format([[[1, 2, 3], [3, 4]], [[5, 6], [7, 8]]], expected_size_all_axes=[2, 2, None])[0]
    assert not Problem.check_format([[[1, 2], [3, 4]], [[5, 6], [7, 8]]], expected_size_all_axes=[2, 2, 3])[0]

def test_problem3_json_serialization():
    # Create an instance of Problem3
    original = Problem3(a=8, b=9, n=13)
    
    # Convert to JSON
    json_data = original.to_json()
    
    # Verify JSON structure
    assert "config" in json_data
    assert "param_values" in json_data
    
    # Verify parameter values
    assert json_data["param_values"] == {
        "a": 8,
        "b": 9,
        "n": 13
    }
    
    # Verify config values
    assert json_data["config"]["name"] == "usamts-1998-4-1"
    assert json_data["config"]["parameters"] == ["a", "b", "n"]
    
    # Reconstruct from JSON
    reconstructed = Problem3.from_json(json_data)
    
    # Verify reconstructed object has same attributes
    assert reconstructed.a == original.a
    assert reconstructed.b == original.b
    assert reconstructed.n == original.n
    assert reconstructed.config.name == original.config.name
    assert reconstructed.config.parameters == original.config.parameters

def test_problem3_json_roundtrip():
    # Test that a problem can be serialized and deserialized without losing information
    original = Problem3(a=6, b=7, n=5)
    json_data = original.to_json()
    reconstructed = Problem3.from_json(json_data)
    
    # Test that the reconstructed problem behaves the same
    test_solution = "67676"  # Some valid solution for testing
    assert original.check_raw(test_solution) == reconstructed.check_raw(test_solution)

def test_invalid_json_structure():
    # Test handling of invalid JSON structure
    invalid_data = {
        "params_values": {"a": 8, "b": 9, "n": 13}
        # Missing "param_values" key
    }
    
    with pytest.raises(KeyError):
        Problem3.from_json(invalid_data)

def test_invalid_parameters():
    # Test handling of invalid parameters
    invalid_data = {
        "config": Problem3.config.__dict__,
        "param_values": {
            "a": 8,
            "b": 9
            # Missing "n" parameter
        }
    }
    
    with pytest.raises(TypeError):
        Problem3.from_json(invalid_data)

def test_generated_problem_serialization():
    # Test that a generated problem can be serialized and deserialized
    generated = Problem3.generate()
    json_data = generated.to_json()
    reconstructed = Problem3.from_json(json_data)
    
    assert reconstructed.a == generated.a
    assert reconstructed.b == generated.b
    assert reconstructed.n == generated.n

def test_original_problem():
    original = Problem3.get_original()
    assert original.check_raw(original.config.original_solution)

    json_data = original.to_json()
    reconstructed = Problem3.from_json(json_data)
    assert reconstructed.check_raw(original.config.original_solution)


def test_generate_instances():
    problems = Problem3.generate_instances(10)
    assert len(problems) == 10
    problems = Problem10.generate_instances(5)
    assert len(problems) == 5
    with pytest.raises(ValueError):
        problems = Problem10.generate_instances(15)

def test_problem_str():
    problem = Problem3(6, 7, 13)
    assert "6" in str(problem)
    assert "7" in str(problem)
    assert "13" in str(problem)
