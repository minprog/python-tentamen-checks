from checkpy import *

from _forbidden_constructs import module_has_syntax_error

def augment(define_location: int, lines: list[str]) -> tuple[str, int, int]:
    # start with the line that was provided
    start = define_location

    # try to go up from that line until empty line or indented line
    while True:
        start -= 1
        if start <= 0:
            start = 0
            break
        elif lines[start].strip() == "":
            start += 1
            break
        elif lines[start].startswith("  ") or lines[start].startswith("\t"):
            break

    name = lines[start].strip()

    # again, start with the line that was provided
    end = define_location

    # try to go down from that line
    waiting = False
    while True:
        end += 1
        if end > len(lines) - 1:
            # EOF reached
            if waiting != False:
                # end = waiting
                end = len(lines) - 1
            else:
                end = len(lines) - 1
            break
        elif lines[end].strip() == "":
            # blank line found
            if waiting == False:
                waiting = end-1
            continue
        elif (lines[end].startswith("  ") or
                lines[start].startswith("\t") or
                lines[start-1].endswith("\\")):
            # indented code line found, belongs to this function
            waiting = False
            continue
        else:
            # non-indented code probably means end of this function
            if waiting:
                end = waiting
            else:
                end -= 1
            break

    return (name, start, end)

def map_functions(source):
    size = len(source)
    if size == 0:
        return []

    # find all function defs
    defs = []
    for i in range(size):
        if source[i].startswith('def '):
            defs.append(i)

    # make list of all start-end line pairs of functions
    augmented = [augment(define, source) for define in defs]
    return augmented

def do_remove_syntax_errors(test):
    filename = test.fileName
    syntax_errors: list[tuple[str, int]] = []

    while error_line := module_has_syntax_error():
        # re-read the file
        with open(filename, 'r') as f:
            current_source: list[str] = f.readlines()
        function_map = map_functions(current_source)

        # correction
        error_line -= 1

        # stop if we apparently already tried to remove this error but it did not succeed
        if error_line in [line for (name, line) in syntax_errors]:
            return

        # stop if we already have 4 funcs with syntax errors commented out
        if len(syntax_errors) == 4:
            return

        # find function boundaries for error line
        for (name, start, end) in function_map:
            if error_line >= start and error_line <= end:
                comment_start, comment_end = start, end
                syntax_errors.append((name, error_line))

        # rewrite file with function commented out
        with open(filename, 'w') as f:
            for lineno in range(len(current_source)):
                if lineno >= comment_start and lineno <= comment_end:
                    f.write(f"# {current_source[lineno]}")
                else:
                    f.write(f"{current_source[lineno]}")

    return syntax_errors

@test()
def remove_syntax_errors(test):
    """verwijderen van eventuele syntax errors"""

    removed_functions = do_remove_syntax_errors(test)

    if removed_functions == []:
        test.description = "geen syntax errors"
        return

    removed_functions_list = ''.join([
        f"      - {name} at line {line}\n" for (name, line) in removed_functions
    ])

    test.description = (
        f"!! syntax error verwijderd in functie(s) !!\n"
        f"{removed_functions_list}\n"
        f"   deze functie(s) kan dus niet gecheckt worden"
    )
