import checkpy.tests as t

import subprocess

@t.test()
def mypy_ok(test):
    """type hints zijn ingevuld en consistent bevonden"""
    def testMethod():
        p = subprocess.run(['mypy', '--strict', '--ignore-missing-imports', '--disable-error-code=name-defined', test.fileName], capture_output=True, universal_newlines=True)
        return p.returncode == 0, p.stdout
    test.test = testMethod
    def report(output):
        lines = []
        for i in output.splitlines()[:-1]:
            text = ':'.join(i.split(':')[1:])[:60]
            lines.append(f"- line {text}")
            if "Missing return statement" in text:
                lines.append("  Watch out with this error! Did you specify the correct return type?")
            if "No return value expected" in text:
                lines.append("  You specified None as the return type but the function returns something.")
        return "\n".join(lines)
    test.fail = report
