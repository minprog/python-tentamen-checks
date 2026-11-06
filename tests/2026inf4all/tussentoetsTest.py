# allow import of common modules from the parent directory
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from checkpy import *
from _pyprog_tools import *

from _catch_syntax_error import remove_syntax_errors
from _catch_infinite_loops import remove_infinite_loops

# standard checks but without pycodestyle!
from _python_checks import forbidden_constructs, mypy_strict, doctest
forbidden_constructs.disallow_all()

@test(10)
def test_split_capitalized (test):
    """1. split_capitalized werkt correct"""
    func = get_defined_function("split_capitalized")
    assert no_input_output_in_function(func)
    assert func(['Amsterdam', 'fiets', 'Utrecht', '']) == [['Amsterdam', 'Utrecht'], ['fiets', '']]
    assert func(['1A', 'Ab']) == [['Ab'], ['1A']]
    assert func(['B', 'b', 'A', 'a']) == [['B', 'A'], ['b', 'a']]
    assert func(['ABC', 'aBC']) == [['ABC'], ['aBC']]
    assert func([' A']) == [[], [' A']]
    assert func(['a', 'b']) == [[], ['a', 'b']]
    assert func(['A', 'B']) == [['A', 'B'], []]
    assert func(['']) == [[], ['']]
    assert func([]) == [[], []]

@test(10)
def test_repeat_chars (test):
    """2. repeat_chars werkt correct"""
    func = get_defined_function("repeat_chars")
    assert no_input_output_in_function(func)
    assert func('abcd', [2, 0, 3]) == 'aacccd'
    assert func('xy', [1, 1]) == 'xy'
    assert func('a', [5]) == 'aaaaa'
    assert func('aa', [2, 1]) == 'aaa'
    assert func('abc', [0]) == 'bc'
    assert func('ab', [0, 0]) == ''
    assert func('ab', [2, 3, 4]) == 'aabbb'
    assert func('xyz', []) == 'xyz'
    assert func('', [4]) == ''
    assert func('', []) == ''

@test(10)
def test_peak_positions (test):
    """3. peak_positions werkt correct"""
    func = get_defined_function("peak_positions")
    assert no_input_output_in_function(func)
    assert func([1, 3, 2, 5]) == [1, 3]
    assert func([1, 2, 1, 2, 1]) == [1, 3]
    assert func([5, 1, 9]) == [0, 2]
    assert func([1, 2, 3]) == [2]
    assert func([3, 2, 1]) == [0]
    assert func([-3, -1, -2]) == [1]
    assert func([5, 1]) == [0]
    assert func([1, 5]) == [1]
    assert func([4, 4, 1]) == []
    assert func([1, 4, 4]) == []
    assert func([1, 2, 2, 1]) == []
    assert func([3, 3]) == []
    assert func([7]) == [0]
    assert func([]) == []

@test(10)
def test_reverse_long_words (test):
    """4. reverse_long_words werkt correct"""
    func = get_defined_function("reverse_long_words")
    assert no_input_output_in_function(func)
    assert func('dit is een lange zin.', 3) == 'dit is een egnal zin.'
    assert func('dit is een lange zin.', 0) == 'tid si nee egnal niz.'
    assert func('lange zin.', 3) == 'egnal zin.'
    assert func('een twee.', 3) == 'een eewt.'
    assert func('Lange Zin.', 2) == 'egnaL niZ.'
    assert func('kort.', 3) == 'trok.'
    assert func('kort.', 4) == 'kort.'
    assert func('kort.', 10) == 'kort.'
    assert func('a b.', 0) == 'a b.'
    assert func('', 3) == ''

@test(10)
def test_select_containing (test):
    """5. select_containing werkt correct"""
    func = get_defined_function("select_containing")
    assert no_input_output_in_function(func)
    assert func(['kaas', 'appel', 'vla'], 'la') == ['appel', 'vla']
    assert func(['vla', 'appel'], 'la') == ['vla', 'appel']
    assert func(['kaas', 'vis'], 'a') == ['kaas']
    assert func(['appel', 'vla'], 'ap') == ['appel']
    assert func(['abc', 'bc'], 'ab') == ['abc']
    assert func(['abc', 'ab', 'a'], 'abc') == ['abc']
    assert func(['vla', 'vis'], 'aa') == ['vla']
    assert func(['kaas', 'vis'], 'xyz') == []
    assert func(['', 'a'], 'a') == ['a']
    assert func(['kaas', 'vis'], '') == ['kaas', 'vis']
    assert func(['', 'a'], '') == ['', 'a']
    assert func([], 'a') == []
    assert func([], '') == []
