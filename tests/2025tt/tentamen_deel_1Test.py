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
def test_select_short_words (test):
    """1. select_short_words werkt correct"""
    assert function_defined_in_module("select_short_words")
    func = get_function("select_short_words")
    assert no_input_output_in_function(func)
    assert func(['zo', 'vergaat', 'des', 'werelds', 'roem'], 4) == ['zo', 'des']
    assert func(['ZO'], 4) == ['ZO']
    assert func([''], 0) == []
    assert func(['rariteitenkabinet', 'dan'], 18) == ['rariteitenkabinet', 'dan']

@test(10)
def test_check_username (test):
    """2. check_username werkt correct"""
    assert function_defined_in_module("check_username", "check_usernames")
    func = get_function("check_username", "check_usernames")
    assert no_input_output_in_function(func)
    assert func('mstgm1') == True
    assert func('1mstgm') == True
    assert func('ms1tgm') == True
    assert func('ms12gm') == False
    assert func('1mstgm2') == False
    assert func('mstgm1 ') == False
    assert func('') == False

@test(10)
def test_select_ordered_words (test):
    """3. select_ordered_words werkt correct"""
    assert function_defined_in_module("select_ordered_words", "select_orderd_words", "selected_ordered_words", "select_ordend_words")
    func = get_function("select_ordered_words", "select_orderd_words", "selected_ordered_words", "select_ordend_words")
    assert no_input_output_in_function(func)
    assert func(["chimps", "adders", "elephants"]) == ["chimps", "adders"]
    assert func(["elephants", "ohmy"]) == []
    assert func([]) == []

@test(10)
def test_extract_number (test):
    """4. extract_number werkt correct"""
    assert function_defined_in_module("extract_number", "extract_numbers", "extract_nummber")
    func = get_function("extract_number", "extract_numbers", "extract_nummber")
    assert no_input_output_in_function(func)
    assert func('Dat kost 200 EUR voor 3 personen') == 200
    assert func('200') == 200
    assert func('') == -1
    assert func('Dat kost 200 EUR') == 200

@test(10)
def test_word_lengths (test):
    """5. word_lengths werkt correct"""
    assert function_defined_in_module("word_lengths", "word_lenghts", "word_length", "select_palindrome")
    func = get_function("word_lengths", "word_lenghts", "word_length", "select_palindrome")
    assert no_input_output_in_function(func)
    assert func('Van harte gefeliciteerd!') == [3, 5, 13]
    assert func('Van gefeliciteerd harte!') == [3, 13, 5]
    assert func('Van!') == [3]
    # assert func('') == []
    # assert func('Noord-Holland') == [5, 7]
