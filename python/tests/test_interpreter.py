import pytest

from scheme.interpreter import seval, create_global_env


@pytest.mark.parametrize(
    "ast,result",
    (
        (("+", 1, 2), 3),
        (("+", ("+", 1, 2), 7), 10),
        (("-", 5, 2), 3),
        (("-", 2), -2),
        (("+", ("-", 2, 3), 5), 4),
        (("*", 0, 3), 0),
        (("*", 3, 0), 0),
        (("*", 1, 3), 3),
        (("*", 3, 1), 3),
        (("*", 12, 4), 48),
        (("/", 12, 3), 4),
        (("/", 12, 5), 2.4),
    ),
)
def test_simple_arithmetic(ast, result):
    env = create_global_env()
    assert seval(ast, env) == result


@pytest.mark.parametrize(
    "ast,result",
    (
        [("and", True, True), True],
        [("and", True, False), False],
        [("and", False, True), False],
        [("and", False, False), False],
        [("or", True, True), True],
        [("or", True, False), True],
        [("or", False, True), True],
        [("or", False, False), False],
        [("not", True), False],
        [("not", False), True],
        [("and", ("or", True, False), True), True],
    ),
)
def test_simple_booleans(ast, result):
    env = create_global_env()
    assert seval(ast, env) == result


def test_define():
    env = create_global_env()
    define_ast = ("define", "foo", ("+", 1, 2))
    seval(define_ast, env)
    assert seval(("+", "foo", 11), env) == 14


LAMBDA_CASES = [
    ["incr", ("x",), ("+", "x", 1), (21,), 22],
    ["add", ("x", "y"), ("+", "x", "y"), (21, 22), 43],
]


@pytest.mark.parametrize("lambda_name,header,body,args,result", LAMBDA_CASES)
def test_lambda(lambda_name, header, body, args, result):
    env = create_global_env()

    lambda_expr = ("lambda", header, body)

    # inline
    assert seval((lambda_expr, *args), env) == result

    # with define
    define_ast = ("define", lambda_name, lambda_expr)
    seval(define_ast, env)
    assert seval((lambda_name, *args), env) == result


@pytest.mark.parametrize("proc_name,header,body,args,result", LAMBDA_CASES)
def test_function_define(proc_name, header, body, args, result):
    env = create_global_env()

    define_ast = ("define", proc_name, header, body)
    seval(define_ast, env)
    assert seval((proc_name, *args), env) == result


def test_lambda_closure():

    env = create_global_env()

    expr = ("lambda", ("x",), ("lambda", ("y",), ("+", "x", "y")))
    proc_name = "curried_add"
    seval(("define", proc_name, expr), env)

    add4 = "add4"

    seval(("define", add4, (proc_name, 4)), env)

    assert seval((add4, 7), env) == 11

    assert seval((add4, 100), env) == 104
