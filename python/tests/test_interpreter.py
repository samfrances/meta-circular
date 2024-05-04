from scheme.interpreter import seval, create_global_env

def test_simple_addition():
    env = create_global_env()
    ast = ["+", 1, 2]
    assert seval(ast, env) == 3


def test_nested_addition():
    env = create_global_env()
    ast = ["+", ["+", 1, 2], 7]
    assert seval(ast, env) == 10


def test_define():
    env = create_global_env()
    define_ast = ["define", "foo", ["+", 1, 2]]
    seval(define_ast, env)
    assert seval(["+", "foo", 11], env) == 14
