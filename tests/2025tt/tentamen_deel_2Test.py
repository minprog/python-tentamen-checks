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

@test()
def no_keys_method_used() -> bool:
    """.keys() method is niet gebruikt"""
    tree = ast.parse(static.getSource())
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
            if n.func.attr in ['keys']:
                raise AssertionError(
                    f"de method keys() mocht niet gebruikt worden!")
    return True

@test(10)
def test_get_all_keys (test):
    """1. get_all_keys werkt correct"""
    assert function_defined_in_module("get_all_keys")
    func = get_function("get_all_keys")
    assert no_input_output_in_function(func)
    assert func([{'hoi': 1, 'doei': 2}, {'10': 'aa'}]) == {'hoi', '10', 'doei'}
    # assert func(['ZO'], 4) == ['ZO']
    # assert func([''], 0) == []
    # assert func(['rariteitenkabinet', 'dan'], 18) == ['rariteitenkabinet', 'dan']

@test(10)
def test_get_column (test):
    """2. get_column werkt correct"""
    assert function_defined_in_module("get_column", "get_columns")
    func = get_function("get_column", "get_columns")
    assert no_input_output_in_function(func)
    assert func([[0,4,3], [2,3,8], [8,10,2]], 2) == [3, 8, 2]
    assert func([[0,9,3], [2,12,8], [8,4,2]], 1) == [9, 12, 4]
    assert func([[0], [2]], 0) == [0, 2]
    assert func([[1]], 0) == [1]

import subprocess

@test(11)
def require_doctests_for_all_functions(test):
    """doctest-overzicht"""
    p = subprocess.run([sys.executable or 'python3', '-m', 'doctest', '-v', test.fileName], capture_output=True, universal_newlines=True)
    raise AssertionError(
        doctest_to_table(
            p.stdout,
            module_name="tentamen_deel_2",
            class_order=["TaskList", "Book", "Library", "Date"]
        )
    )


import re
from typing import List, Dict, Tuple, Optional


def doctest_to_table(
    report: str,
    module_name: str,
    class_order: Optional[List[str]] = None,
) -> str:
    """
    Table columns:
      Class | Method | Is tested | Success

    Rules:
    - Skip the main module itself.
    - Ignore module-level functions entirely.
    - Include class-level items (Method="") and class methods.
    - If class_order is provided, order classes by that list.
    - If any class in class_order is missing from doctest items, still include it
      as a single row: Class=<name>, Method="", Is tested="no", Success="-".
    """

    no_tests_items: List[str] = []
    passed_items: List[str] = []
    failed_items: List[str] = []

    lines = report.splitlines()

    def gather_block(start_idx: int):
        out, i = [], start_idx
        while i < len(lines) and lines[i].startswith((" ", "\t")):
            out.append(lines[i].strip())
            i += 1
        return i, out

    i = 0
    while i < len(lines):
        s = lines[i].strip()

        if re.match(r"^\d+\s+items?\s+had\s+no\s+tests:", s):
            i, b = gather_block(i + 1)
            no_tests_items.extend(b)
            continue

        if re.match(r"^\d+\s+items?\s+passed\s+all\s+tests:", s):
            i, b = gather_block(i + 1)
            passed_items.extend(b)
            continue

        if re.match(r"^\d+\s+items?\s+had\s+failures:", s):
            i, b = gather_block(i + 1)
            failed_items.extend(b)
            continue

        i += 1

    def extract_target(s: str) -> str:
        # "2 tests in tentamen_deel_2.Book.__str__" -> "tentamen_deel_2.Book.__str__"
        m = re.search(r"\bin\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)+)\s*$", s)
        return m.group(1) if m else s

    passed_targets = [extract_target(x) for x in passed_items]
    failed_targets = [extract_target(x) for x in failed_items]

    def split_target(full: str) -> Tuple[str, str]:
        # skip module itself
        if full == module_name:
            return "", ""

        parts = full.split(".")
        if len(parts) < 2:
            return "", ""

        tail = parts[1:]  # drop module prefix

        # Only accept class and class members; ignore module-level functions
        if not tail[0][:1].isupper():
            return "", ""

        cls = tail[0]
        meth = ".".join(tail[1:]) if len(tail) > 1 else ""  # "" means class-level
        return cls, meth

    statuses: Dict[Tuple[str, str], Dict[str, Optional[bool]]] = {}

    def set_status(full: str, tested: bool, success: Optional[bool]):
        cls, meth = split_target(full)
        if cls == "" and meth == "":
            return
        key = (cls, meth)
        statuses.setdefault(key, {"tested": None, "success": None})
        statuses[key]["tested"] = tested
        if success is not None:
            statuses[key]["success"] = success

    for t in no_tests_items:
        set_status(t, tested=False, success=None)

    for t in passed_targets:
        set_status(t, tested=True, success=True)

    for t in failed_targets:
        set_status(t, tested=True, success=False)

    # ---- Ensure missing specified classes appear as one "not there" row ----
    if class_order:
        present_classes = {cls for (cls, _meth) in statuses.keys()}
        for cls in class_order:
            if cls not in present_classes:
                statuses.setdefault((cls, ""), {"tested": False, "success": None})

    # ---- Build rows ----
    rows = []
    for (cls, meth), st in statuses.items():
        rows.append({
            "Class": cls,
            "Method": meth,
            "Is tested": "yes" if st["tested"] else "-",
            "Success": (
                "v" if st["success"] is True else
                "x" if st["success"] is False else
                "-"
            )
        })

    # ---- Sort: class_order first, then remaining classes alphabetically ----
    order_index = {c: i for i, c in enumerate(class_order or [])}
    def class_rank(c: str) -> Tuple[int, str]:
        return (order_index.get(c, len(order_index)), c)

    rows.sort(key=lambda r: (
        class_rank(r["Class"]),
        r["Method"] != "",   # class-level (empty method) first
        r["Method"],
    ))

    # ---- Format table ----
    headers = ["Class", "Method", "Is tested", "Success"]
    widths = {h: len(h) for h in headers}
    for r in rows:
        for h in headers:
            widths[h] = max(widths[h], len(r[h]))

    def fmt_row(r):
        return " | ".join(r[h].ljust(widths[h]) for h in headers)

    sep = "-+-".join("-" * widths[h] for h in headers)

    return "\n".join(
        [fmt_row(dict(zip(headers, headers))), sep] +
        [fmt_row(r) for r in rows]
    )


# Example (your failing-only-functions report):
# print(doctest_to_table(DOCTEST_OUTPUT, "tentamen_deel_2", ["Book", "Date", "Library", "TaskList"]))
#
# This will include 4 rows (one per class) all marked Is tested="no", Success="-"
# because only module-level functions were present and those are ignored.
