from _pyprog_tools import *

import checkpy

@test(0)
def remove_main(test):
    """voorbewerking van het bestand voor testen"""
    # lees file via checkpy API, voeg weer \n toe na splitten
    file_contents = [f"{x}\n" for x in checkpy.static.getSource().split("\n")]

    # wat het echt doet is het verwijderen van alle code die niet
    # in een functie staat, maar wel pas vanaf de eerste functie
    # (zodat dingen als imports en globals wel bewaard blijven mits
    # ze boven de bovenste functie staan)
    with open(checkpy.file.name, 'w') as f:
        state = 0
        for line in file_contents:
            if state == 0:
                if line.startswith('def '):
                    state = 1
                f.write(line)
            elif state == 1:
                if not (line.strip() == '' or line.startswith(' ') or line.startswith("\t") or line.startswith("def ") or line.startswith("#")):
                    state = 2
                    continue
                f.write(line)
            elif state == 2:
                if line.startswith('def '):
                    f.write(line)
                    state = 1

    # debug code
    # with open(checkpy.file.name, 'r') as f:
    #     print(f.read())


@test(0)
def remove_syntax_error(test):
    """verwijderen van eventuele syntax error"""
    line = module_has_syntax_error()
    if line == False:
        test.description = "geen syntax errors"
        return

    # lees file via checkpy API, voeg weer \n toe na splitten
    file_contents = [f"{x}\n" for x in checkpy.static.getSource().split("\n")]

    # zoek eerste 'def'-regel boven de foutregel
    def_line = None
    for i in range(line - 1, -1, -1):
        if file_contents[i].lstrip().startswith("def "):
            def_line = i
            break

    next_def_line = None
    for i in range(line, len(file_contents)):
        if file_contents[i].lstrip().startswith("def "):
            next_def_line = i
            break

    if next_def_line is None:
        next_def_line = len(file_contents)

    test.description = (
        f"!! syntax error verwijderd in functie !!\n"
        f"      {file_contents[def_line].strip()}\n"
        f"   deze functie kan dus niet gecheckt worden"
    )

    with open(checkpy.file.name, 'w') as f:
        for lineno in range(len(file_contents)):
            if lineno >= def_line and lineno < next_def_line:
                f.write(f"# {file_contents[lineno]}")
            else:
                f.write(file_contents[lineno])
