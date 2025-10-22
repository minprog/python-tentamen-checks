import checkpy.tests as t
import checkpy.lib as lib
import checkpy.assertlib as assertlib

from _pyprog_tools import *

import sys
import subprocess
import re
import os

def pl(n: int, desc: str):
    meervouden = {
        'voorbeeld': 'voorbeelden',
        'functie': 'functies',
        'testbare functie': 'testbare functies',
        'slaagt': 'slagen'
    }
    if n == 1:
        return f"1 {desc}"
    else:
        return f"{n} {meervouden[desc]}"

def function_stats(source):
    functions = re.findall(r'def\s+(\w+)\s*\(([^\)]*)\) *(->\s*([\w\|\s\[,\] _]+))?:', source)
    n_functions_not_returning = len([function for function in functions if (
        'file' in function[1] or  # function name contains 'file'
        function[3] == 'None' or  # function type is None
        function[3] == ''         # function type is omitted?
    )])
    n_functions = len(functions)
    return n_functions, n_functions_not_returning

def doctest_stats(filename):
    # run doctest and extract results
    p = subprocess.run([sys.executable or 'python3', '-m', 'doctest', '-v', filename], capture_output=True, universal_newlines=True)

    if "Traceback" in p.stderr:
        return False, p.stderr.splitlines()[-1]

    test_stats_rex = re.compile(r'(\d*) tests? in (\d*) items?')
    test_stats = test_stats_rex.search(p.stdout.splitlines()[-3])

    test_pass_rex = re.compile(r'(\d*) passed')
    test_pass = test_pass_rex.search(p.stdout.splitlines()[-2])

    # number of classes/functions reported by doctest (-1 is for module)
    n_items_doctested = int(test_stats.group(2))-1

    # number of doctests found anywhere
    n_doctests = int(test_stats.group(1))

    # number of tests passed
    n_doctests_passed = int(test_pass.group(1))

    return n_items_doctested, n_doctests, n_doctests_passed

def check_doctests(test, test_not_returning=True):
    # retrieve functions from source
    with open(test.fileName, 'r') as source_file:
        source = source_file.read()
        n_functions, n_functions_not_returning = function_stats(source)

    # bail out if no functions at all
    if n_functions == 0:
        return False, "je programma moet functies gebruiken (of type hints ontbreken!)"

    n_items_doctested, n_doctests, n_doctests_passed = doctest_stats(test.fileName)

    if not test_not_returning:
        n_items_doctested -= n_functions_not_returning

    # if n_items_doctested == 0:
    #     # geen testbare functies blijkbaar?
    #     return True

    # test ratio
    if n_items_doctested > 0 and n_doctests // n_items_doctested < 2:
        return False, f"{pl(n_doctests, 'voorbeeld')} bij {pl(n_items_doctested, 'functie')} is niet genoeg"

    if n_doctests_passed < n_doctests:
        return False, f"{n_doctests_passed} van {pl(n_doctests, 'voorbeeld')} geslaagd"

    if test_not_returning:
        test.description = f"doctests: {n_doctests} goedgekeurd voor {pl(n_items_doctested, 'functie')}"
    else:
        test.description = f"doctests: {n_doctests} goedgekeurd voor {pl(n_items_doctested, 'testbare functie')}"

    return True

@t.test(2)
def require_doctests_for_all_functions(test):
    """elke functie heeft voldoende doctests en ze geven allemaal akkoord"""
    def testMethod():
        return check_doctests(test, True)
    test.test = testMethod
    test.fail = lambda info: info
    test.timeout = lambda: 120

@t.test(2)
def require_doctests_for_returning_functions(test):
    """doctests zijn voldoende aanwezig en ze geven allemaal akkoord"""
    def testMethod():
        return check_doctests(test, False)
    test.test = testMethod
    test.fail = lambda info: info
    test.timeout = lambda: 120
