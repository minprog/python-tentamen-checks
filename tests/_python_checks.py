"""
Unified import surface for course Python checks.

Usage:
    from _python_checks import checkstyle, forbidden_constructs, mypy_strict, check_doctests
    forbidden_constructs.disallow_all()
"""

# Re-export with the names you want to use at call sites
from _basic_checkstyle import basic_style as checkstyle
from _forbidden_constructs import check_forbidden_constructs as forbidden_constructs
from _mypy_strict import mypy_ok as mypy_strict
from _check_doctests import require_doctests_for_returning_functions as doctest
from _check_doctests import require_doctests_for_all_functions as doctest_all

__all__ = [
    "checkstyle",
    "forbidden_constructs",
    "mypy_strict",
    "doctest",
    "doctest_all"
]
