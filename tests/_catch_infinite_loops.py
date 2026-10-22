import os
import re
import subprocess
import sys

from checkpy import *

from _catch_syntax_error import map_functions

# seconds that the doctests of the student file may run before we stop them
DOCTEST_SECONDS = 8

# maximum number of functions that get commented out
MAX_REMOVED = 4

# runs doctest on a file and makes Python print the stack of the running
# code and exit if it takes too long, which tells us where it is stuck
RUNNER = (
    "import faulthandler, runpy, sys\n"
    "faulthandler.dump_traceback_later({seconds}, exit=True)\n"
    "sys.argv = ['doctest', {filename!r}]\n"
    "runpy.run_module('doctest', run_name='__main__')\n"
)

def find_stuck_line(filename: str) -> int | None:
    """
    Runs the doctests and returns the line in the file where the code was
    stuck, or None if the doctests finished in time (or if it is unclear
    where they got stuck).
    """
    try:
        p = subprocess.run(
            [sys.executable or 'python3', '-c',
             RUNNER.format(seconds=DOCTEST_SECONDS, filename=filename)],
            capture_output=True, universal_newlines=True,
            timeout=DOCTEST_SECONDS + 10
        )
    except subprocess.TimeoutExpired:
        return None

    if "Timeout (" not in p.stderr:
        return None

    # the stack is printed with the most recent call first, so the first
    # frame that belongs to the student file is where the code was stuck
    here = os.path.realpath(filename)
    for path, lineno in re.findall(r'File "([^"]+)", line (\d+) in', p.stderr):
        if os.path.realpath(path) == here:
            return int(lineno)

    return None

def do_remove_infinite_loops(test) -> list[tuple[str, int]]:
    """
    Comments out each function in which the doctests get stuck and returns
    the name and line number for every function that was removed.
    """
    filename = test.fileName
    stuck: list[tuple[str, int]] = []

    while len(stuck) < MAX_REMOVED:
        # line numbers are 1-based, the function map is 0-based
        stuck_line = find_stuck_line(filename)
        if stuck_line is None:
            break
        stuck_line -= 1

        # stop if we already tried to remove this line but it did not help
        if stuck_line in [line for (name, line) in stuck]:
            break

        with open(filename, 'r') as f:
            current_source: list[str] = f.readlines()

        # find function boundaries for the line where the code is stuck
        comment_range = None
        for (name, start, end) in map_functions(current_source):
            if start <= stuck_line <= end:
                comment_range = (start, end)
                stuck.append((name, stuck_line))

        # stop if the stuck line is not inside a function
        if comment_range is None:
            break

        # rewrite file with function commented out
        with open(filename, 'w') as f:
            for lineno in range(len(current_source)):
                if comment_range[0] <= lineno <= comment_range[1]:
                    f.write(f"# {current_source[lineno]}")
                else:
                    f.write(current_source[lineno])

    return stuck

@test(timeout=90)
def remove_infinite_loops(test):
    """verwijderen van eventuele oneindige loops"""

    removed_functions = do_remove_infinite_loops(test)

    if removed_functions == []:
        test.description = "geen oneindige loops"
        return

    removed_functions_list = ''.join([
        f"      - {name} at line {line + 1}\n" for (name, line) in removed_functions
    ])

    test.description = (
        f"!! oneindige loop verwijderd in functie(s) !!\n"
        f"{removed_functions_list}\n"
        f"   deze functie/class/if(s) kan dus niet gecheckt worden"
    )
