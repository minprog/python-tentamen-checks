import checkpy.tests as t

import subprocess
import re
import os

@t.test()
def basic_style(test):
    """formatting is goed genoeg"""
    def testMethod():
        # run pycodestyle for a couple of basic checks
        try:
            max_line_length = os.environ['MAX_LINE_LENGTH']
        except KeyError:
            max_line_length = 99
        try:
            max_doc_length = os.environ['MAX_DOC_LENGTH']
        except KeyError:
            max_doc_length = 79
        p = subprocess.run([
                'pycodestyle',
                '--select=E101,E112,E113,E115,E116,E501,E502,W505',
                f"--max-line-length={max_line_length}",
                f"--max-doc-length={max_doc_length}",
                test.fileName
            ], capture_output=True, universal_newlines=True)
        if p.returncode != 0:
            if "E1" in p.stdout:
                test.fail = lambda info : f"let op juiste indentatie!\nheb je misschien op één plek te veel of te weinig\nspaties aan het begin van de regel? (meestal 0, 4, 8, ...)"
                return False, p.stdout
            if "E501" in p.stdout or "W505" in p.stdout:
                test.fail = lambda info : f"regel(s) te lang, code max {max_line_length} tekens, comments max {max_doc_length} tekens"
                return False, p.stdout
            if "E502" in p.stdout:
                test.fail = lambda info: f"gebruik tussen haakjes geen \\ om de regel af te breken"
                return False, p.stdout
            # if "W291" in p.stdout:
            #     pattern = r'[^:\n]+:(\d+):\d+: W291'
            #     matches = re.findall(pattern, p.stdout)
            #     test.fail = lambda info: f"zorg dat er geen spaties aan het eind van een regel staan (regel {', '.join(matches)})"
            #     return False, p.stdout
        return True
    test.test = testMethod
