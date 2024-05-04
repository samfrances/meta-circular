from ..interpreter import seval, create_global_env

def test_one():
    env = create_global_env()
    ast = ["+", 1, 2]
    assert seval(ast, env) == 3
