from scheme.parser import parse, MissingClosingParenError
from scheme.interpreter import seval, create_global_env

global_env = create_global_env()

awaiting_further_input = False
expr_str = ""

while True:

    if awaiting_further_input:
        expr_str += " " + input("    ")
    else:
        expr_str = input("> ")

    try:
        for parsed in parse(expr_str):
            result = seval(parsed, global_env)
            awaiting_further_input = False
        if result is not None:
            print(result)
    except MissingClosingParenError as e:
        awaiting_further_input = True
        continue
    except Exception as e:
        print(e)
