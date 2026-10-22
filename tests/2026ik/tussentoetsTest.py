# allow import of common modules from the parent directory
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from checkpy import *
from _pyprog_tools import *

from _catch_syntax_error import remove_syntax_errors

# standard checks but without pycodestyle!
from _python_checks import forbidden_constructs, mypy_strict, doctest
forbidden_constructs.disallow_all()

@test(10)
def test_count_below_above (test):
    """1. count_below_above werkt correct"""
    func = get_defined_function("count_below_above")
    assert no_input_output_in_function(func)
    assert func([3, 8, 5, 10, 1], 5) == [2, 2]
    assert func([1, 2, 3], 10) == [3, 0]
    assert func([10, 20], 5) == [0, 2]
    assert func([5, 5], 5) == [0, 0]
    assert func([-3, 0, 3], 0) == [1, 1]
    assert func([], 5) == [0, 0]

@test(10)
def test_bracket_depth (test):
    """2. bracket_depth werkt correct"""
    func = get_defined_function("bracket_depth")
    assert no_input_output_in_function(func)
    assert func('(a(b)c)(d)') == 2
    assert func('(()') == -1
    assert func('()') == 1
    assert func('((()))') == 3
    assert func('(a)(b)') == 1
    assert func('()(') == -1
    assert func('(') == -1
    assert func('abc') == 0
    assert func('') == 0

@test(10)
def test_count_pairs (test):
    """3. count_pairs werkt correct"""
    func = get_defined_function("count_pairs")
    assert no_input_output_in_function(func)
    assert func([1, 4, 2, 3], 5) == 2
    assert func([2, 2, 2], 4) == 3
    assert func([1, 2, 3, 4], 5) == 2
    assert func([3, 3], 6) == 1
    assert func([0, 0], 0) == 1
    assert func([-1, 1, 0], 0) == 1
    assert func([1, 2, 3], 10) == 0
    assert func([5], 10) == 0
    assert func([], 0) == 0

@test(10)
def test_select_by_letter_count (test):
    """4. select_by_letter_count werkt correct"""
    func = get_defined_function("select_by_letter_count", "select_by_letter")
    assert no_input_output_in_function(func)
    assert func(['banaan', 'appel', 'aap'], 'a', 2) == ['aap']
    assert func(['banaan', 'appel', 'aap'], 'a', 3) == ['banaan']
    assert func(['appel', 'aap'], 'p', 2) == ['appel']
    assert func(['kaas', 'vis'], 'a', 0) == ['vis']
    assert func(['Aap', 'aap'], 'a', 2) == ['aap']
    assert func(['banaan', 'appel'], 'z', 0) == ['banaan', 'appel']
    assert func(['banaan', 'appel'], 'z', 1) == []
    assert func(['', 'x'], 'x', 0) == ['']
    assert func([''], 'x', 1) == []
    assert func([], 'a', 1) == []

@test(10)
def test_hashtags (test):
    """5. hashtags werkt correct"""
    func = get_defined_function("hashtags", "hastags")
    assert no_input_output_in_function(func)
    assert func('ik #hou van #python') == ['hou', 'python']
    assert func('#eerste en #laatste') == ['eerste', 'laatste']
    assert func('ik hou van #python') == ['python']
    assert func('#python') == ['python']
    assert func('#a #b #c') == ['a', 'b', 'c']
    assert func('geen tags hier') == []
    assert func('python') == []
    assert func('') == []
