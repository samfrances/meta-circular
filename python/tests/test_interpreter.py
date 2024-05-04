from ..interpreter import seval, create_global_env

def test_simple_addition():
    env = create_global_env()
    ast = ["+", 1, 2]
    assert seval(ast, env) == 3


def test_nested_addition():
    env = create_global_env()
    ast = ["+", ["+", 1, 2], 7]
    assert seval(ast, env) == 10
