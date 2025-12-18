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
    doctest_output = subprocess.run([sys.executable or 'python3', '-m', 'doctest', '-v', test.fileName], capture_output=True, universal_newlines=True)
    mypy_output = subprocess.run(['mypy', '--strict', '--ignore-missing-imports', '--disable-error-code=name-defined', test.fileName], capture_output=True, universal_newlines=True)
    # raise AssertionError(mypy_output.stdout)
    raise AssertionError(
        build_test_type_overview(
            doctest_report=doctest_output.stdout,
            mypy_output=mypy_output.stdout,
            source=static.getSource(),
            module_name="tentamen_deel_2",
            class_order=["TaskList", "Book", "Library", "Date"],
            include_module_level_functions=True,   # brings back get_all_keys/get_column rows too
        )
        # doctest_to_table(
        #     p.stdout,
        #     module_name="tentamen_deel_2",
        #     class_order=["TaskList", "Book", "Library", "Date"]
        # )
    )

import ast
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


# -----------------------------
# 1) Parse doctest summary -> statuses
# -----------------------------

def parse_doctest_statuses(
    report: str,
    module_name: str,
    include_module_level_functions: bool = True,
) -> Dict[Tuple[str, str], Dict[str, Optional[bool]]]:
    """
    Returns: {(class, method): {"tested": bool, "success": Optional[bool]}}
    - class="" and method="funcname" for module-level functions (if included)
    - class="Book" method="" for class-level items
    - class="Book" method="__str__" for methods
    - module itself is excluded
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
        m = re.search(r"\bin\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)+)\s*$", s)
        return m.group(1) if m else s

    passed_targets = [extract_target(x) for x in passed_items]
    failed_targets = [extract_target(x) for x in failed_items]

    def split_target(full: str) -> Tuple[str, str]:
        if full == module_name:
            return "", ""

        parts = full.split(".")
        if len(parts) < 2:
            return "", ""

        tail = parts[1:]  # drop module

        # class or class.member
        if tail[0][:1].isupper():
            cls = tail[0]
            meth = ".".join(tail[1:]) if len(tail) > 1 else ""
            return cls, meth

        # module-level function
        if include_module_level_functions:
            return "", tail[0]

        return "", ""

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

    return statuses


# -----------------------------
# 2) Parse mypy output -> line diagnostics
# -----------------------------


@dataclass(frozen=True)
class MypyDiag:
    file: str
    line: int
    kind: str   # "error" | "note" | "warning"
    msg: str
    code: str   # e.g. "type-arg", may be ""

def parse_mypy_output(mypy_text: str) -> List[MypyDiag]:
    """
    Parses mypy output like:
      tentamen_deel_2.py:59: error: Function is missing a return type annotation  [no-untyped-def]
    """
    diags: List[MypyDiag] = []

    # file:line: kind: message [code]
    rx = re.compile(
        r"^(?P<file>[^:]+):(?P<line>\d+):\s*(?P<kind>error|note|warning):\s*"
        r"(?P<msg>.*?)(?:\s+\[(?P<code>[^\]]+)\])?\s*$",
        re.IGNORECASE,
    )

    for raw in mypy_text.splitlines():
        s = raw.strip()
        if not s:
            continue
        if s.lower().startswith("found ") and " errors " in s.lower():
            continue

        m = rx.match(s)
        if not m:
            continue

        diags.append(MypyDiag(
            file=m.group("file"),
            line=int(m.group("line")),
            kind=m.group("kind").lower(),
            msg=m.group("msg").strip(),
            code=(m.group("code") or "").strip(),
        ))

    return diags

# -----------------------------
# 3) Map line -> (class, method) using AST
# -----------------------------

@dataclass
class DefSpan:
    cls: str            # "" for module-level function
    name: str           # function name or "" for class body
    start: int
    end: int

class _SpanCollector(ast.NodeVisitor):
    def __init__(self):
        self.spans: List[DefSpan] = []
        self._class_stack: List[str] = []

    def visit_ClassDef(self, node: ast.ClassDef):
        cls_name = node.name
        start = getattr(node, "lineno", 1)
        end = getattr(node, "end_lineno", start)
        # class body span (to attribute errors inside class body, not inside a method)
        self.spans.append(DefSpan(cls=cls_name, name="", start=start, end=end))

        self._class_stack.append(cls_name)
        self.generic_visit(node)
        self._class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef):
        cls = self._class_stack[-1] if self._class_stack else ""
        start = getattr(node, "lineno", 1)
        end = getattr(node, "end_lineno", start)
        self.spans.append(DefSpan(cls=cls, name=node.name, start=start, end=end))
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.visit_FunctionDef(node)  # treat same

def build_line_owner_map(source: str) -> Dict[int, Tuple[str, str]]:
    """
    Returns mapping: line_number -> (class, method)
      - module-level function: ("", "func")
      - class method: ("Book", "__str__")
      - class body (outside any method): ("Book", "")
      - otherwise: ("", "") (module/global code)
    """
    tree = ast.parse(source)
    collector = _SpanCollector()
    collector.visit(tree)

    spans = sorted(
        collector.spans,
        key=lambda s: (s.start, -(s.end - s.start))  # prefer narrower later via scan below
    )

    # For each line, choose the narrowest enclosing span (method beats class body).
    line_to_owner: Dict[int, Tuple[str, str]] = {}
    max_line = max((getattr(tree, "end_lineno", 1),), default=1)

    # Determine max line from source text if end_lineno missing
    max_line = max(max_line, source.count("\n") + 1)

    for line in range(1, max_line + 1):
        owners = [sp for sp in spans if sp.start <= line <= sp.end]
        if not owners:
            line_to_owner[line] = ("", "")
            continue
        # pick narrowest (smallest span length); if tie, prefer function (name != "")
        owners.sort(key=lambda sp: ((sp.end - sp.start), 0 if sp.name != "" else 1))
        best = owners[0]
        line_to_owner[line] = (best.cls, best.name)

    return line_to_owner


# -----------------------------
# 4) Merge into one table (with ordering and "missing classes" rows)
# -----------------------------

def format_overview_table(
    doctest_statuses: Dict[Tuple[str, str], Dict[str, Optional[bool]]],
    mypy_diags: List[MypyDiag],
    source: str,
    class_order: Optional[List[str]] = None,
    include_module_level_functions: bool = True,
) -> str:
    line_owner = build_line_owner_map(source)

    # aggregate mypy diagnostics per (class, method)
    issues: Dict[Tuple[str, str], List[MypyDiag]] = defaultdict(list)
    for d in mypy_diags:
        cls, meth = line_owner.get(d.line, ("", ""))
        if cls == "" and meth == "" and not include_module_level_functions:
            continue
        # if it's module-level global code, we don't show it in this overview
        if cls == "" and meth == "":
            continue
        if cls == "" and meth != "" and not include_module_level_functions:
            continue
        issues[(cls, meth)].append(d)

    # build combined keyset
    combined_keys = set(doctest_statuses.keys()) | set(issues.keys())

    # If class_order is provided, ensure missing classes appear as one row.
    if class_order:
        present_classes = {cls for (cls, _m) in combined_keys if cls}
        for cls in class_order:
            if cls not in present_classes:
                combined_keys.add((cls, ""))

    def yesno(x: Optional[bool]) -> str:
        return "yes" if x else "no"

    rows = []
    for (cls, meth) in combined_keys:
        # Skip module itself (already), and optionally module-level functions
        if cls == "" and meth == "":
            continue
        if cls == "" and meth != "" and not include_module_level_functions:
            continue

        dt = doctest_statuses.get((cls, meth))
        tested = dt["tested"] if dt and dt["tested"] is not None else False
        success = dt["success"] if dt else None

        di = issues.get((cls, meth), [])
        has_mypy = bool([x for x in di if x.kind == "error"]) or bool(di)
        # You can decide if you only want "error" to count; currently counts any diag (error/note).
        mypy_count = len(di)

        rows.append({
            "Class": cls,
            "Method": meth,
            # "Is tested": "yes" if tested else "-",
            "doctest OK": "yes" if success is True else "no" if success is False else "-",
            "mypy err": str(mypy_count) if mypy_count else '',
        })

    order_index = {c: i for i, c in enumerate(class_order or [])}

    def class_rank(c: str) -> Tuple[int, str]:
        # Put module-level functions first
        if c == "":
            return (-1, "")  # anything smaller than 0
        return (order_index.get(c, len(order_index)), c)

    rows.sort(key=lambda r: (
        class_rank(r["Class"]),
        0 if r["Method"] == "" else 1,  # class-level rows first
        r["Method"],
    ))

    headers = ["Class", "Method", "doctest OK", "mypy err"]
    widths = {h: len(h) for h in headers}
    for r in rows:
        for h in headers:
            widths[h] = max(widths[h], len(r[h]))

    def fmt_row(r):
        return " | ".join(r[h].ljust(widths[h]) for h in headers)

    sep = "-+-".join("-" * widths[h] for h in headers)

    return "\n".join([fmt_row(dict(zip(headers, headers))), sep] + [fmt_row(r) for r in rows])


# -----------------------------
# Convenience wrapper
# -----------------------------

def build_test_type_overview(
    doctest_report: str,
    mypy_output: str,
    source: str,
    module_name: str,
    class_order: Optional[List[str]] = None,
    include_module_level_functions: bool = True,
) -> str:
    dt = parse_doctest_statuses(
        doctest_report,
        module_name=module_name,
        include_module_level_functions=include_module_level_functions,
    )
    my = parse_mypy_output(mypy_output)
    return format_overview_table(
        doctest_statuses=dt,
        mypy_diags=my,
        source=source,
        class_order=class_order,
        include_module_level_functions=include_module_level_functions,
    )
