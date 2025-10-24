# allow import common modules from the parent directory
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from checkpy import *
from _pyprog_tools import *

# this comments out a single function if it has a syntax error
# but does not comment out any further problems :-)
from _remove_main import remove_syntax_error

# standard checks but without pycodestyle!
from _python_checks import forbidden_constructs, mypy_strict, doctest
forbidden_constructs.disallow_all()

@test(10)
def test_is_sorted (test):
    """1. is_sorted werkt correct"""
    assert function_defined_in_module("is_sorted")
    func = get_function("is_sorted")
    assert no_input_output_in_function(func)
    assert func([1, 2, 3]) == True
    # assert func([]) == True # niet vermeld in de opdracht
    assert func([3, 2, 1]) == False
    assert func([3, 6, 1, 10]) == False
    assert func([1, 2, 0]) == False

@test(10)
def test_password_check (test):
    """2. password_check werkt correct"""
    assert function_defined_in_module("password_check")
    func = get_function("password_check")
    assert no_input_output_in_function(func)
    assert func('Rariteit22') == True
    assert func('rariteit22') == False
    assert func('Rariteit2') == False
    assert func('Rariteit') == False

@test(10)
def test_count_words_in_list (test):
    """3. count_words_in_list werkt correct"""
    assert function_defined_in_module("count_words_in_list")
    func = get_function("count_words_in_list")
    assert no_input_output_in_function(func)
    assert func("Ik eet", ["Ik", "kaas", "brood"]) == 1
    assert func("Ik eet kaas", ["Ik", "kaas", "brood"]) == 2
    assert func("Ik", ["Ik", "kaas", "brood"]) == 1
    assert func("", ["Ik", "kaas", "brood"]) == 0
    assert func("Ik eet kaas", ["Ik", "brood"]) == 1
    assert func("Ik eet kaas", ["brood"]) == 0
    assert func("Ik eet kaas", []) == 0
    assert func("", []) == 0
    assert func("Ik eet  kaas", ["Ik", "kaas", "brood"]) == 2

@test(10)
def test_parameterize (test):
    """4. parameterize werkt correct"""
    assert function_defined_in_module("parameterize", "parametize", 'parametrize')
    func = get_function("parameterize", "parametize", 'parametrize')
    assert no_input_output_in_function(func)
    assert func('Kaas + Worst') == 'kaas_worst'
    assert func('kaas') == 'kaas'
    assert func('Kaas') == 'kaas'
    assert func('Kaas worst') == 'kaas_worst'
    assert func('') == ''

@test(10)
def test_words_with_double_letters (test):
    """5. words_with_double_letters werkt correct"""
    assert function_defined_in_module("words_with_double_letters")
    func = get_function("words_with_double_letters")
    assert no_input_output_in_function(func)
    assert func(['Rotterdam', 'Den Bosch', 'Schoorl']) == ['Rotterdam', 'Schoorl']
    assert func(['Rotterdam', 'Den Bosch', 'Schoorl']) == ['Rotterdam', 'Schoorl']
    assert func(['Den Bosch', 'Schoorl']) == ['Schoorl']
    assert func(['Rotterdam', 'Schoorl']) == ['Rotterdam', 'Schoorl']
    assert func(['Rotterdam', 'Den Bosch']) == ['Rotterdam']
    assert func(['Den Bosch']) == []
    assert func(['Amsterdam', 'Den Helder']) == []
    assert func(['']) == []
    assert func([]) == []
