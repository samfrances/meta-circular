
from src.parser import parse
from src.interpreter import seval, create_global_env

global_env = create_global_env()

while True:

    expr_str = input("> ")
    try:
        for parsed in parse(expr_str):
            result = seval(parsed, global_env)
        if result is not None:
            print(result)
    except Exception as e:
        print(e)
