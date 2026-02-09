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
def test_select_not_immune (test):
    """1. select_not_immune werkt correct"""
    assert function_defined_in_module("select_not_immune")
    func = get_function("select_not_immune")
    assert no_input_output_in_function(func)
    assert func(['GTCAA', 'GAGAA', 'CAAATG']) == ['GTCAA', 'GAGAA']
    assert func(['CAAATG', 'GTCAA', 'GAGAA']) == ['GTCAA', 'GAGAA']
    assert func(['AAATG', 'GTCAA', 'GAGAA']) == ['GTCAA', 'GAGAA']
    assert func(['CAAATG']) == []
    assert func(['']) == ['']

@test(10)
def test_check_high_num (test):
    """2. check_high_num werkt correct"""
    assert function_defined_in_module("check_high_num", "check_high_nums")
    func = get_function("check_high_num", "check_high_nums")
    assert no_input_output_in_function(func)
    assert func('ik bied 100,-') == True
    assert func('ik bied 10,-') == True
    assert func('ik bied 1,-') == False
    assert func('ik bied 1,- plus 2,-') == False
    assert func('') == False

@test(10)
def test_remove (test):
    """3. remove werkt correct"""
    assert function_defined_in_module("remove")
    func = get_function("remove")
    assert no_input_output_in_function(func)
    assert func("de groene kamer", "groene") == 'de  kamer'
    assert func("de groene kamer", "") == 'de groene kamer'
    assert func("de kamer", "") == 'de kamer'
    assert func("de kamer", "de") == ' kamer'
    assert func("", "de") == ''

@test(10)
def test_normalize_spacing (test):
    """4. normalize_spacing werkt correct"""
    assert function_defined_in_module("normalize_spacing")
    func = get_function("normalize_spacing")
    assert no_input_output_in_function(func)
    assert func('  Voorzitter,   dit is een gotspe') == 'Voorzitter, dit is een gotspe'
    assert func('  Voorzitter,   dit is een gotspe   ') == 'Voorzitter, dit is een gotspe'
    assert func('  Voorzitter') == 'Voorzitter'
    assert func('  Voor  zitter     ') == 'Voor zitter'
    assert func('  ') == ''

@test(10)
def test_longest_seq (test):
    """5. longest_seq werkt correct"""
    assert function_defined_in_module("longest_seq")
    func = get_function("longest_seq")
    assert no_input_output_in_function(func)
    assert func('GGTCGGAAACCTTT') == 'AAA'
    assert func('GGTCGGAACCTTT') == 'TTT'
    assert func('GGGTCGGAAACCTTT') == 'GGG'
    assert func('AAA') == 'AAA'
