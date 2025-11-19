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
def test_select_not_lower (test):
    """1. select_not_lower werkt correct"""
    assert function_defined_in_module("select_not_lower")
    func = get_function("select_not_lower")
    assert no_input_output_in_function(func)
    assert func(['Roep', 'maar', 'HALLO']) == ['Roep', 'HALLO']
    assert func(['Roep', 'HALLo']) == ['Roep', 'HALLo']
    assert func(['raam']) == []
    assert func(['raam', 'gordijn']) == []
    assert func([]) == []

@test(10)
def test_string_picker (test):
    """2. string_picker werkt correct"""
    assert function_defined_in_module("string_picker", "string_pickers")
    func = get_function("string_picker", "string_pickers")
    assert no_input_output_in_function(func)
    assert func(['a', 'dd'], [0, 0, 1]) == 'aadd'
    assert func(['a', 'dd'], [1]) == 'dd'
    assert func(['a', 'dd'], [0]) == 'a'
    assert func(['a', 'dd'], [0, 0, 0, 0]) == 'aaaa'
    assert func(['dd', 'a'], [1, 0, 0, 0]) == 'adddddd'
    assert func(['dd', 'a'], []) == ''
    assert func([], []) == ''

@test(10)
def test_remove_prefix (test):
    """3. remove_prefix werkt correct"""
    assert function_defined_in_module("remove_prefix")
    func = get_function("remove_prefix")
    assert no_input_output_in_function(func)
    assert func('toedeloe', 'toe') == 'deloe'
    assert func('toedeloe', 'toet') == 'toedeloe'
    assert func('toedeloe', 't') == 'oedeloe'
    assert func('toets', 'toe') == 'ts'
    assert func('toets', '') == 'toets'
    assert func('', 'raar') == ''
    assert func('', '') == ''

@test(10)
def test_most_vowely_word (test):
    """4. most_vowely_word werkt correct"""
    assert function_defined_in_module("most_vowely_word", "most_vowely_words", "most_vowels_word")
    func = get_function("most_vowely_word", "most_vowely_words", "most_vowels_word")
    assert no_input_output_in_function(func)
    assert func('de groene kamer') == 'groene'
    assert func('groene') == 'groene'
    assert func('amsterdam') == 'amsterdam'
    assert func('Amsterdam') == 'Amsterdam'
    assert func('Amsterdam rotterdam') == 'rotterdam'
    assert func('roep mij') == 'roep'
    assert func('mij roep') == 'roep'
    assert func('kaas taart') == 'taart'

@test(10)
def test_select_palindromes (test):
    """5. select_palindromes werkt correct"""
    assert function_defined_in_module("select_palindromes", "select_palidromes", "select_palindrome")
    func = get_function("select_palindromes", "select_palidromes", "select_palindrome")
    assert no_input_output_in_function(func)
    assert func(['lepel', 'spoon', 'ada', 'Raar']) == ['lepel', 'ada']
    assert func(['lepel']) == ['lepel']
    assert func(['spoon']) == []
    assert func(['parterretrap', 'kaaszaak']) == ['parterretrap']
    assert func([]) == []
