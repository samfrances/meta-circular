import sys

from scheme.parser import parse, MissingClosingParenError
from scheme.interpreter import seval, create_global_env

with open(sys.argv[1], "r") as f:
    global_env = create_global_env()
    tree = []
    input = ""
    final_parse_error = None
    for line in f:
        try:
            input += " " + line
            for parsed in parse(input):
                tree.append(parsed)
            final_parse_error = None
        except MissingClosingParenError as e:
            final_parse_error = e
            continue
        else:
            input = ""

    if final_parse_error is not None:
        raise final_parse_error

    for exp in tree:
        seval(exp, global_env)
