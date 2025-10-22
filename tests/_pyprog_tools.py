from checkpy import *
import ast

from checkpy import static

def module_has_syntax_error():
    try:
        compile(static.getSource(), "<your program>", "exec")
    except SyntaxError as error:
        return error.lineno
    return False

# ---- assertion helpers ----

def function_defined_in_module(expected_name: str, *alternatives: list[str]) -> bool:
    defs = static.getFunctionDefinitions()
    check = any(
        name in defs for name in [expected_name, *alternatives]
    )
    if not check:
        raise AssertionError(f"`{expected_name}` is niet aanwezig")
    return check

def function_not_defined_in_module(name: str) -> bool:
    check = name not in static.getFunctionDefinitions()
    if not check:
        raise AssertionError(f"`{name}` is onverwacht aanwezig")
    return check

def construct_not_in_ast(construct: type):
    # check for literals of that type
    check = construct in static.AbstractSyntaxTree()
    name = str(construct).split(".")[1].split("'")[0].lower()
    # check for construction call of that type (!)
    call_check = call_in_module(name)
    if check or call_check:
        if name in ['list', 'set', 'tuple', 'dict']:
            raise AssertionError(f"{name}s mogen niet gebruikt worden in deze opdracht")
        elif name == 'slice':
            raise AssertionError(f"slicing mag niet gebruikt worden in deze opdracht")
        else:
            raise AssertionError(f"`{name}` mag niet gebruikt worden in deze opdracht")
    return True

def construct_in_ast(construct: type):
    check = construct in static.AbstractSyntaxTree()
    name = str(construct).split(".")[1].split("'")[0].lower()
    if not check:
        raise AssertionError(f"`{name}` moet gebruikt worden in deze opdracht")
    return check

def no_string_methods_used() -> bool:
    """
    Filters string methods that do a search
    (we would like students to loop instead)
    """
    tree = ast.parse(static.getSource())
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
            if n.func.attr in ['replace', 'find', 'index']:
                raise AssertionError(
                    f"string-methods zoals {n.func.attr}() "
                    f"mogen niet gebruikt worden")
    return True

def no_string_mult_used() -> bool:
    tree = ast.parse(static.getSource())
    for n in ast.walk(tree):
        if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Mult):
            if (isinstance(n.left, ast.Constant) and isinstance(n.left.value, str)
                or isinstance(n.right, ast.Constant) and isinstance(n.right.value, str)):
                raise AssertionError(f"`*` mag alleen gebruikt worden om getallen te vermenigvuldigen met elkaar")
    return True

def no_input_output_in_function(f):
    if 'print' in f._function.__code__.co_names or 'input' in f._function.__code__.co_names:
        raise AssertionError(
            "deze functie zou geen print of input moeten hebben")
    return True

def no_print_return_in_function(f):
    try:
        construct_not_in_ast(ast.Return)
    except AssertionError:
        raise AssertionError(
            "deze functie zou geen print of return moeten hebben")
    if 'print' in f._function.__code__.co_names:
        raise AssertionError(
            "deze functie zou geen print of return moeten hebben")
    return True

# ---- analysis helpers (no AssertionError on failure) ----

def string_in_module(*forbidden_strings):
    source = static.getSource()
    return any(f in source for f in forbidden_strings)

def call_in_module(*banned_calls) -> bool:
    found = False

    class Visitor(ast.NodeVisitor):
        def visit_Name(self, node: ast.Name):
            if node.id in banned_calls:
                nonlocal found
                found = True

    calls: list[ast.Call] = static.getAstNodes(ast.Call)
    for call in calls:
        Visitor().visit(call)

    return found

# ---- run() wraps output of running a module into a class ----
# ---- it keeps track of the stdin that was used and also  ----
# ---- exposes several string ops like strip()             ----

import re

class RunResult(str):
    def __new__(cls, value: str, **metadata):
        obj = super().__new__(cls, value)
        obj._metadata = dict(metadata)
        return obj

    @property
    def metadata(self) -> dict:
        return self._metadata

    # --- utilities ---------------------------------------------------------
    def with_meta(self, **extra) -> "RunResult":
        """Return a copy with updated/merged metadata."""
        return RunResult(self, **{**self._metadata, **extra})

    def _wrap(self, value, **extra):
        """
        Re-wrap string-like results as RunResult, preserving/merging metadata.
        Recurses into tuples/lists and wraps any str elements.
        """
        meta = {**self._metadata, **extra}
        if isinstance(value, str):
            return RunResult(value, **meta)
        if isinstance(value, tuple):
            return tuple(self._wrap(v, **extra) for v in value)
        if isinstance(value, list):
            return [self._wrap(v, **extra) for v in value]
        return value  # e.g., ints, floats, bytes, None, etc.

    # --- custom helpers ----------------------------------------------------
    def number(self, index: int = 0, pattern: str = r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?") -> "RunResult":
        """
        Extract the Nth number substring as a RunResult (preserving metadata).
        Raises ValueError if no such number exists.
        """
        matches = re.findall(pattern, self)
        if index < 0:
            index += len(matches)
        if not (0 <= index < len(matches)):
            # raise ValueError("No matching number found at that index.")
            return self._wrap('')
        return self._wrap(matches[index])

    # --- operations that should obviously preserve subclass ----------------
    def __getitem__(self, key):
        # slicing or single-char access
        return self._wrap(super().__getitem__(key))

    def strip(self, chars: str | None = None) -> "RunResult":
        return self._wrap(super().strip(chars))

    def lstrip(self, chars: str | None = None) -> "RunResult":
        return self._wrap(super().lstrip(chars))

    def rstrip(self, chars: str | None = None) -> "RunResult":
        return self._wrap(super().rstrip(chars))

    def __add__(self, other):
        return self._wrap(super().__add__(other))

    def __radd__(self, other):
        return self._wrap(str(other) + str(self))

    def __mul__(self, n: int):
        return self._wrap(super().__mul__(n))

    def __rmul__(self, n: int):
        return self._wrap(super().__rmul__(n))

    # --- dynamic wrapping for most other str methods -----------------------
    def __getattr__(self, name: str):
        """
        For str methods not explicitly overridden, fetch the corresponding
        function from str and wrap its output if it returns strings/collections.
        """
        attr = getattr(str, name, None)
        if callable(attr):
            def method(*args, **kwargs):
                result = attr(self, *args, **kwargs)
                return self._wrap(result)
            return method
        raise AttributeError(name)

    def __eq__(self, other):
        """
        Compare actual and expected output.

        - If expected_display is None: do direct equality check with expected.
        - If expected_display is given: interpret expected as a regex pattern string,
          and expected_display as the value to show in error messages.
        """
        actual = self
        actual_str = str(actual)
        expected = other
        expected_display = None

        # Normalize expected into string form
        if isinstance(expected, re.Pattern):
            match = expected.match(actual_str)
            expected = expected.pattern
        elif expected_display is not None:
            match = re.match(expected, actual_str)
        else:
            match = (self.__str__() == expected)

        expected_str = expected_display or expected

        if not match:
            if 'stdin' in self.metadata:
                stdin_str = ' ⏎ '.join(self.metadata['stdin'])
                input_msg = f"gegeven input: {stdin_str} ⏎\n"
            else:
                input_msg = ""
            if len(expected_str.__repr__()) + len(self.__repr__()) > 40:
                raise AssertionError(
                    f"{input_msg}"
                    f"verwachte output is:\n"
                    f"  {expected_str!r}\n"
                    f"maar kreeg:\n"
                    f"  {actual!r}"
                )
            else:
                raise AssertionError(
                    f"{input_msg}"
                    f"verwachte output is {expected_str!r} maar kreeg {actual!r}"
                )

        return True

    def match(self, pattern, display=None):
        stdin_str = ' ⏎ '.join(self.metadata['stdin'])
        expected_str = display or pattern
        if not isinstance(pattern, re.Pattern):
            pattern = re.compile(pattern)
        try:
            self.__eq__(pattern)
        except AssertionError:
            raise AssertionError(
                f"gegeven input: {stdin_str} ⏎\n"
                f"verwachte output is {expected_str!r} maar kreeg {self!r}"
            )
        return True

from checkpy.entities import exception

def run(*stdin) -> str:
    stdin = [str(a) for a in stdin]
    try:
        output = outputOf(stdinArgs=stdin, overwriteAttributes = [("__name__", "__main__")])
    except exception.InputError:
        raise AssertionError(
            f"gegeven input: {' ⏎ '.join(stdin)} ⏎\n"
            "het programma bleef hierna toch nog om input vragen")
    return RunResult(
        output,
        stdin=stdin
    )

# ---- Wrapper classes for testing function return values and neatly reporting ----

import functools

class TestableValue:
    """
    Wraps a value so it can be tested against an expected
    value and then neatly reports failure.
    """
    def __init__(self, value, function_name, function_args):
        # the value originating from a function call
        self.value = value

        # how the function was called in a check
        self._function_call_repr = (
            f"bij een aanroep van {function_name}"
            f"({', '.join([x.__repr__() for x in function_args])})"
        )

    def __eq__(self, other):
        # check the original value and report if not equal
        if self.value != other:
            feedback_string = (
                f"{self._function_call_repr}: "
                f"verwachtte {other!r} maar kreeg {self.value!r}"
            )
            if len(feedback_string) > 60:
                feedback_string = (
                    f"{self._function_call_repr}:\n"
                    f"  verwachtte {other!r}\n"
                    f"  maar kreeg {self.value!r}"
                )
            raise AssertionError(feedback_string)
        return True

class TestableCallable:
    """
    Wraps a function to store name and wrap the result of a call
    into TestableValue for further test reporting.
    """
    def __init__(self, func):
        self._func = func
        functools.update_wrapper(self, func)

    def __call__(self, *args, **kwargs):
        return TestableValue(self._func(*args, **kwargs), self._func.name, args)

def fname(*cands):
    defs = static.getFunctionDefinitions()
    for cand in cands:
        if cand in defs:
            return cand
    raise AssertionError(f"function {cands[0]} not found in code")

def get_function(default_name, *alternatives):
    """
    Retrieve function and wrap into TestableCallable, so that a call
    result will be wrapped in TestableValue.
    """
    name = fname(default_name, *alternatives)

    # Actually, the function is already wrapped in a checkpy Function object
    # but we can wrap that once more.
    f = getFunction(name)
    return TestableCallable(f)
