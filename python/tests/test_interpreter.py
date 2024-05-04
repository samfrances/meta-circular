import pytest

from scheme.interpreter import seval, create_global_env


@pytest.mark.parametrize(
    "ast,result",
    (
        (["+", 1, 2], 3),
        (["+", ["+", 1, 2], 7], 10),
        (["-", 5, 2], 3),
        (["-", 2], -2),
        (["+", ["-", 2, 3], 5], 4),
        (["*", 0, 3], 0),
        (["*", 3, 0], 0),
        (["*", 1, 3], 3),
        (["*", 3, 1], 3),
        (["*", 12, 4], 48),
        (["/", 12, 3], 4),
        (["/", 12, 5], 2.4),
    ),
)
def test_simple_arithmetic(ast, result):
    env = create_global_env()
    assert seval(ast, env) == result


def test_nested_addition():
    env = create_global_env()
    ast = ["+", ["+", 1, 2], 7]
    assert seval(ast, env) == 10


def test_define():
    env = create_global_env()
    define_ast = ["define", "foo", ["+", 1, 2]]
    seval(define_ast, env)
    assert seval(["+", "foo", 11], env) == 14
