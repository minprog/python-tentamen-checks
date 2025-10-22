"""
Reusable checkpy module for forbidden constructs, with grouped rules.

Usage:
    import forbidden_construct_checker as fcc

    # Only groups:
    fcc.disallow(groups=["functional", "strings_advanced"])

    # Only specific rules:
    fcc.disallow(rules=["eval", "tabs"])

    # Groups + rules:
    fcc.disallow(groups=["typing_old"], rules=["eval"])

    # Clear selection (no rules active):
    fcc.disallow()

    check_forbidden_constructs = fcc.check_forbidden_constructs
"""

from typing import Callable, Iterable
from checkpy import static
import ast

import checkpy.tests as t
from _pyprog_tools import (
    string_in_module, call_in_module,
    no_string_methods_used, no_string_mult_used, construct_not_in_ast
)

def import_in_module(*banned_imports) -> bool:
    imports: list[ast.Import] = static.getAstNodes(ast.Import)
    for imp in imports:
        names = [alias.name for alias in imp.names]
        for name in names:
            if name in banned_imports:
                return True

    imports_from: list[ast.ImportFrom] = static.getAstNodes(ast.ImportFrom)
    for imp in imports_from:
        if imp.module in banned_imports:
            return True

    return False

def has_generators() -> bool:
    return static.getAstNodes(ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)

# --- single source of truth: groups -> rules ---
RULE_GROUPS: dict[str, dict[str, tuple[Callable[[], bool], str]]] = {
    "basic_formatting": {
        "tabs": (lambda: string_in_module("\t"), "let op dat je geen tabs gebruikt"),
    },
    "deprecations": {
        "Optional": (lambda: string_in_module("Optional"), "gebruik ... | None i.p.v. Optional[...]"),
        "List": (lambda: string_in_module("List["), "gebruik list[...] i.p.v. List[...]"),
        "Tuple": (lambda: string_in_module("Tuple["), "gebruik tuple[...] i.p.v. Tuple[...]"),
        "Dict": (lambda: string_in_module("Dict["), "gebruik dict[...] i.p.v. Dict[...]"),
        "Set": (lambda: string_in_module("Set["), "gebruik set[...] i.p.v. Set[...]"),
    },
    # "string_builtins": {
    #     "stringmult": (lambda: not no_string_mult_used(), "gebruik geen string * getal"),
    #     "stringmethods": (lambda: not no_string_methods_used(), "gebruik geen string-methods"),
    # },
    "list_builtins": {
        "min_max": (lambda: call_in_module("min", "max"), "gebruik geen min() of max()"),
        "sorted": (lambda: call_in_module("sorted"), "gebruik geen sorted()"),
    },
    "functional_style": {
        "try": (lambda: not construct_not_in_ast(ast.Try), "mag niet"),
        "map": (lambda: call_in_module("map"), "gebruik geen map()"),
        "zip": (lambda: call_in_module("zip"), "gebruik geen zip()"),
        "generators": (lambda: has_generators(), "let op dat je geen [... for ...] gebruikt"),
        "all_any": (lambda: call_in_module("all", "any"), "gebruik geen all() of any()"),
        "eval": (lambda: call_in_module("eval"), "gebruik geen eval()"),
    },
    "stdlib_restrictions": {
        "import_math": (lambda: import_in_module("math"), "gebruik geen import math"),
        "import_decimal": (lambda: import_in_module("decimal"), "gebruik geen import decimal"),
    },
}

# Derived flat index for validation/lookup
ALL_RULES: dict[str, tuple[Callable[[], bool], str]] = {
    rule: check
    for group in RULE_GROUPS.values()
    for rule, check in group.items()
}

# Active rules (set by disallow())
ACTIVE_RULES: dict[str, tuple[Callable[[], bool], str]] | None = None


def disallow(*, groups: Iterable[str] = (), rules: Iterable[str] = ()) -> None:
    """
    Enable rules from the given groups and/or explicit rule keys.
    Both args default to empty = select nothing.

    Examples:
        disallow(groups=["functional", "strings_advanced"])
        disallow(rules=["eval", "tabs"])
        disallow(groups=["typing_old"], rules=["eval"])
        disallow()  # selects nothing
    """
    global ACTIVE_RULES

    selected: set[str] = set()

    # Validate groups and collect their rules
    groups = list(groups)
    unknown_groups = [g for g in groups if g not in RULE_GROUPS]
    if unknown_groups:
        raise ValueError(f"Unknown group(s): {unknown_groups}")

    for g in groups:
        selected.update(RULE_GROUPS[g].keys())

    # Validate explicit rule keys and add them
    rules = list(rules)
    unknown_rules = [r for r in rules if r not in ALL_RULES]
    if unknown_rules:
        raise ValueError(f"Unknown rule(s): {unknown_rules}")

    selected.update(rules)

    ACTIVE_RULES = {k: ALL_RULES[k] for k in sorted(selected)}


def disallow_all() -> None:
    """Enable all rules."""
    global ACTIVE_RULES
    ACTIVE_RULES = dict(ALL_RULES)


def module_has_syntax_error():
    try:
        compile(static.getSource(), "<your program>", "exec")
    except SyntaxError as error:
        return error.lineno
    return False


@t.test()
def check_forbidden_constructs(test):
    """check op verboden constructies"""
    if ACTIVE_RULES is None:
        raise RuntimeError(
            "forbidden_construct_checker.disallow(...) moet worden "
            "aangeroepen voordat check_forbidden_constructs kan draaien"
        )

    if (lineno := module_has_syntax_error()):
        raise AssertionError(f"de code bevat een syntax error op regel {lineno}")

    for key, (check_fn, message) in ACTIVE_RULES.items():
        if check_fn():
            raise AssertionError(message)

# Expose as methods on the test function
check_forbidden_constructs.disallow = disallow
check_forbidden_constructs.disallow_all = disallow_all
