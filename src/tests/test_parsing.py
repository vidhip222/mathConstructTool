import pytest
from math_construct.parsing import parse_answer, match_list_depth
from fractions import Fraction
from math_construct.problems.imo_shortlist.problem_2001_c5 import Problem17
import pytest
import time
import sympy


def test_problem_parser():
    assert Problem17.parse([{"role": "assistant", "content": r"\boxed{2}"}, {"role": "user", "content": r"\boxed{1}"}]) == [[2]]
    assert Problem17.parse([{"role": "assistant", "content": r"\boxed{2}"}, {"role": "assistant", "content": r"\boxed{3}"}]) == [[3]]
    assert Problem17.parse([{"role": "assistant", "content": r"\boxed{2}"}, {"role": "assistant", "content": r"Great"}]) == [[2]]

def test_ints():
    assert match_list_depth(parse_answer("9101123595505617977528089887640449438202247191011235955056179775280898876404494382022471"), 0) == 9101123595505617977528089887640449438202247191011235955056179775280898876404494382022471
    assert match_list_depth(parse_answer("34334433433440.0000"), 0) == 34334433433440
    assert match_list_depth(parse_answer("34334433433440"), 0) == 34334433433440
    assert match_list_depth(parse_answer("343344334.33440"), 0) == 343344334.33440
    assert match_list_depth(parse_answer("10^{300}"), 0) == 10 ** 300 # best I can do
    assert match_list_depth(parse_answer("10^{1999}"), 0) == 10 ** 1999 # best I can do
    assert match_list_depth(parse_answer(r"9 \cdot 10^{4999}"), 0) == 9 * 10 ** 4999 # best I can do
    assert not match_list_depth(parse_answer(r"9 \cdot 10^{4999}"), 0) == 9 * 10 ** 4999 - 1 # best I can do
    assert match_list_depth(parse_answer(r"9 \cdot 10^{4999} - 1"), 0) == 9 * 10 ** 4999 - 1 # best I can do


    assert match_list_depth(parse_answer("34334433433440", str), 0) == "34334433433440"
    assert match_list_depth(parse_answer("5^3 \\cdot 2"), 0) == 5 ** 3 * 2

def test_primitive_type():
    assert parse_answer("34334433433440", int) == 34334433433440
    with pytest.raises(ValueError):
        parse_answer("b24", int)
    with pytest.raises(ValueError):
        parse_answer("(1,2,3),(4,5,6,b)", int)

def test_depth_conversion():
    assert match_list_depth(parse_answer("\\begin{array}\nb & w &b \\\\\nw&b & w\n\\end{array}", str), 1) == ["bwb", "wbw"]
    assert match_list_depth(parse_answer("\\begin{array}{cc}1 & 7 \\\\ 3 & 1\\end{array}"), 1) == ["17", "31"]
    assert match_list_depth(parse_answer("((2))"), 2) == [[2]]
    assert match_list_depth(parse_answer("((2))"), 0) == 2
    assert match_list_depth(parse_answer("((2)),((2))"), 1) == [2,2]
    assert match_list_depth(parse_answer("(1, 2, 3, 4)"), 2) == [[1, 2, 3, 4]]

def test_lists():
    assert match_list_depth(parse_answer("(1)"), 1) == [1]
    assert match_list_depth(parse_answer("00001111, 00010111", str), 1) == ["00001111", "00010111"]
    assert match_list_depth(parse_answer("1, 2, 3, 4, 5"), 1) == [1, 2, 3, 4, 5]
    assert match_list_depth(parse_answer("1,-2, 3,-4, 5"), 1) == [1, -2, 3, -4, 5]
    assert match_list_depth(parse_answer("[1, 2, 3, 4, 5]"), 1) == [1, 2, 3, 4, 5]
    assert match_list_depth(parse_answer("(1, 2, 3, 4, 5)"), 1) == [1, 2, 3, 4, 5]
    assert match_list_depth(parse_answer(r"522222\n522222\n522222", str), 1) == ["522222", "522222", "522222"]

def test_fractions():
    assert match_list_depth(parse_answer("\\frac{1}{48}, \\frac{1}{96}, \\frac{1}{192}"), 1) == [Fraction(1, 48), Fraction(1, 96), Fraction(1, 192)]
    assert match_list_depth(parse_answer("(\\frac{1}{48}, \\frac{1}{96}), (\\frac{1}{192}, \\frac{1}{96})"), 2) == [[Fraction(1, 48), Fraction(1, 96)], [Fraction(1, 192), Fraction(1, 96)]]
    assert match_list_depth(parse_answer("3, 41, 271, \\frac{10^{295}+2}{3}"), 1) == [3, 41, 271, Fraction(10**295 + 2, 3)]
    assert match_list_depth(parse_answer(r"\left(\frac{1}{7}, \frac{1}{7}\right),\n\left(\frac{1}{7}, \frac{2}{7}\right),"), 2) == [[Fraction(1, 7), Fraction(1, 7)], [Fraction(1, 7), Fraction(2, 7)]]
    assert match_list_depth(parse_answer(r"\left(\frac{1}{7}, \frac{1}{7}\right),\left(\frac{1}{7}, \frac{2}{7}\right),"), 2) == [[Fraction(1, 7), Fraction(1, 7)], [Fraction(1, 7), Fraction(2, 7)]]
    assert match_list_depth(parse_answer(r"0, \frac{1+\sqrt{5}}{2}, 2+\sqrt{5}, \frac{1+\sqrt{5}}{2}"), 1) == [0, (1 + 5 ** 0.5) / 2, 2 + 5 ** 0.5, (1 + 5 ** 0.5) / 2]
    assert parse_answer("\\frac{20}{x}", str) == "\\frac{20}{x}"
    assert parse_answer("\\frac{20}{10^{2000}}", float) == Fraction(20, 10 ** 2000)
    assert parse_answer("-\\frac{20}{100}", float) == Fraction(-20, 100)
    parsed = parse_answer("3, 41, 271, \\frac{10^{295}+2}{3}", Fraction)
    assert all([isinstance(x, Fraction) for x in parsed])
    assert parse_answer("-20/100", Fraction) == Fraction(-20, 100)
    assert parse_answer("1/2,3/4,6/8", Fraction) == [Fraction(1, 2), Fraction(3, 4), Fraction(6, 8)]
    with pytest.raises(ValueError):
        parse_answer("sqrt(2) / 2", Fraction)


def test_list_computations():
    assert match_list_depth(parse_answer("2+\\sqrt{3}, 1, 2+\\sqrt{3}, 1"), 1) == [3.732050807568877, 1.0, 3.732050807568877, 1.0]
    assert match_list_depth(parse_answer("1 / 2 + 1 / 2, 1, 1"), 1) == [1, 1, 1]
    
def test_arrays():
    assert match_list_depth(parse_answer("\\begin{array}{cc}1 & 7 \\\\ 3 & 1\\end{array}"), 2) == [[1, 7], [3, 1]]
    assert match_list_depth(parse_answer("\\begin{array}{cc}1 & 7 \\\\ 3 & 1\\\\ \\end{array}"), 2) == [[1, 7], [3, 1]]
    assert match_list_depth(parse_answer("\\begin{array}1 & 7 \\\\ 3 & 1\\end{array}"), 2) == [[1, 7], [3, 1]]
    assert match_list_depth(parse_answer("\\begin{array}{cc}1 &7 \\\\3&1\\end{array}"), 2) == [[1, 7], [3, 1]]
    assert match_list_depth(parse_answer("\\begin{matrix}1 & 7 \\\\ 3 & 1\\end{matrix}"), 2) == [[1, 7], [3, 1]]
    assert match_list_depth(parse_answer("\\begin{bmatrix}1 & 7 \\\\ 3 & 1\\end{bmatrix}"), 2) == [[1, 7], [3, 1]]
    assert match_list_depth(parse_answer("\\begin{array}{ccc}\nb & w & b \\\\\nw & b & w\n\\end{array}", str), 2) == [["b", "w", "b"], ["w", "b", "w"]]
    assert match_list_depth(parse_answer("\\begin{array}\nb & w &b \\\\\nw&b & w\n\\end{array}", str), 2) == [["b", "w", "b"], ["w", "b", "w"]]

def test_list_of_lists():
    assert match_list_depth(parse_answer("(1), (2, 0)"), 2) == [[1], [2, 0]]
    assert match_list_depth(parse_answer("(1, 2, 1, 0), (2, 0, 2, 0)"), 2) == [[1, 2, 1, 0], [2, 0, 2, 0]]
    assert match_list_depth(parse_answer("(1, 1, 2), (1, 2, 3), (1, 3, 4)"), 2) == [[1, 1, 2], [1, 2, 3], [1, 3, 4]]
    assert match_list_depth(parse_answer("(1, 1, 2], [1, 2,3),(1, 3,4)"), 2) == [[1, 1, 2], [1, 2, 3], [1, 3, 4]]
    assert match_list_depth(parse_answer("[[1, 1, 2], [1, 2,3),(1, 3,4)],[[1,2,3]]"), 3) == [[[1, 1, 2], [1, 2, 3], [1, 3, 4]], [[1, 2, 3]]]
    assert match_list_depth(parse_answer(r"[[1, 1, 2]\n[1, 2,3)\n(1, 3,4)]\n[[1,2,3]]"), 3) == [[[1, 1, 2], [1, 2, 3], [1, 3, 4]], [[1, 2, 3]]]

def test_combos():
    assert match_list_depth(parse_answer("\\begin{array}{cc}1 & 7 \\\\ 3 & 1\\end{array}, 2"), None) == [[[1, 7], [3, 1]], 2]

    assert match_list_depth(parse_answer("\\begin{array}{cc}1 & 7 \\\\ 3 & 1\\end{array}, [2, 3], \\frac{2}{3}"), None) == [[[1, 7], [3, 1]], [2, 3], Fraction(2, 3)]
    assert match_list_depth(parse_answer("\\begin{array}{cc}(1, 2) & (2,3) \\\\ 3 & (1,2)\\end{array}, 2"), None) == [[[[1,2], [2,3]], [3, [1,2]]], 2]
    assert match_list_depth(parse_answer(r"\begin{pmatrix} 1 & 2 \\ 3 & 4 \end{pmatrix}, \begin{pmatrix} 1 & 2 \\ 3 & 4 \end{pmatrix}")) == [[[1, 2], [3, 4]], [[1, 2], [3, 4]]]

def test_real():
    assert parse_answer(r"""\\begin{array}{cccccccc}\" )\n    for i in range(6):\n        row_str = \" & \".join(map(str, [box[i] for box in final_boxes])) + r\"\\\\\"\n        print(row_str)\n    print(r\"\\end{array}}\")\n\nsolve()\n```""") == None
    assert parse_answer("\\{\\{1, 17, 33, 49\\}, \\{2, 18, 34, 50\\}\\}") == [[1, 17, 33, 49], [2, 18, 34, 50]]
    assert parse_answer("\\frac{20}{3} x^{2} - 21x", str) == "\\frac{20}{3} x^{2} - 21x"
    with pytest.raises(ValueError):
        parse_answer("\\frac{20}{3} x^{2} - 21x", float)

    assert match_list_depth(parse_answer(r"\begin{array}{c}\n(1, 4, 9), \\ \n(1, 4, 9)\end{array}", int)) == [[1, 4, 9], [1, 4, 9]]
    assert parse_answer(r"\n\begin{aligned}\n&(1, 1, 1, 1, 1), & (2, 2, 1, 1, 1), \\\n&(3, 1, 3, 1, 1), & (4, 2, 2, 1, 1),\end{aligned}") == [[[1, 1, 1, 1, 1], [2, 2, 1, 1, 1]], [[3, 1, 3, 1, 1], [4, 2, 2, 1, 1]]]
    assert parse_answer("(1, 3), (2, 7), (3, 3)") == [[1, 3], [2, 7], [3, 3]]
    assert parse_answer("3b,b,b,\\frac{1}{3}") == ["3b", "b", "b", Fraction(1, 3)]
    assert round(parse_answer("\\frac{6 \\times \\sqrt{2}}{\\sqrt{23}}"), 2) == round(6 * 2 ** 0.5 / 23 ** 0.5, 2)
    assert parse_answer("(1, 22, 41, 58),\\ (9, 34, 57, 78),\\ (729, 834, 937, 1038)") == [[1, 22, 41, 58], [9, 34, 57, 78], [729, 834, 937, 1038]]
    assert parse_answer("""(2, 36), \\\\\n(3, 34), \\\\\n(4, 5)""") == [[2, 36], [3, 34], [4, 5]]

def test_depth_and_type():
    from math_construct.problems.backups.problem_2014_n4 import ProblemBMO2014N4
    from math_construct.utils import get_depth
    assert ProblemBMO2014N4.get_primitive_type() == int
    assert get_depth(ProblemBMO2014N4.config.original_solution) == 2

def test_complicated_depth():
    assert match_list_depth(parse_answer("(([2, 4), (1, -2]))"), 2) == [[2, 4], [1, -2]]

def test_array_4():
    assert parse_answer(r"\begin{array}{*{2}{c}}0 & 1 \\ 1 & 0 \end{array}") == [[0, 1], [1, 0]]

def test_errors():
    with pytest.raises(ValueError):
        parse_answer("\\\\begin{array}{' + 'c' * N + '}')\nfor row in matrix:\n    print(' & '.join(map(str, row)) + ' \\\\\\\\')\nprint('\\\\end{array}}'", int)


def test_latex():
    assert parse_answer(r"\cos(\frac{2\pi}{9})") == 0.766044443118978
    assert parse_answer(r"\log_8 13") == 1.2334799060470307