from __future__ import annotations

import operator
from typing import Any, Dict, Literal, Tuple, Optional, TypeGuard, Union

from .common import ParsedExpression, ParsedExpressionList


class NullEnvironment:

    def __getitem__(self, key):
        raise KeyError(key)


class Environment:

    _enclosing: Environment | NullEnvironment

    def __init__(self, enclosing: Optional[Environment] = None):
        self._enclosing = NullEnvironment() if enclosing is None else enclosing
        self._table: Dict[str, Any] = {}

    def __getitem__(self, key: str):
        try:
            return self._table[key]
        except KeyError as e:
            return self._enclosing[key]

    def __setitem__(self, key: str, value):
        if key not in self._table:
            raise KeyError(key)
        self._table[key] = value

    def define(self, key: str, value):
        if key in self._table:
            raise Exception(f"'{key}' already defined.")
        self._table[key] = value


def create_global_env():
    env = Environment()
    env.define("+", operator.add)
    env.define("-", lambda x, y=None: -x if y is None else x - y)
    env.define("*", operator.mul)
    env.define("/", operator.truediv)
    env.define("display", lambda x: print(x))
    return env


def seval(exp: ParsedExpression, env: Environment):
    if is_primitive(exp):
        return exp
    if is_symbol(exp):
        return env[exp]
    if is_define_exp(exp):
        return seval_define(exp, env)
    if is_list(exp):
        func_name_or_expr = exp[0]
        func_args = exp[1:]
        return sapply(func_name_or_expr, func_args, env)


def sapply(proc_name: ParsedExpression, proc_args: ParsedExpressionList, env: Environment):
    proc = seval(proc_name, env)
    if not callable(proc):
        raise Exception("Invalid function application")
    args = [seval(a, env) for a in proc_args]
    return proc(*args)


def is_primitive(exp: ParsedExpression) -> float | int:
    return isinstance(exp, float) or isinstance(exp, int)


def is_symbol(exp: ParsedExpression) -> TypeGuard[str]:
    return isinstance(exp, str)


def is_list(exp: ParsedExpression) -> TypeGuard[ParsedExpressionList]:
    return isinstance(exp, tuple)


# Define

VariableDefinition = Tuple[Literal["define"], str, ParsedExpression]


def is_define_exp(exp: ParsedExpression) -> TypeGuard[VariableDefinition]:
    return is_list(exp) and len(exp) == 3 and exp[0] == "define"


def seval_define(exp: VariableDefinition, env: Environment):
    name = exp[1]
    definition = exp[2]
    value = seval(definition, env)
    env.define(name, value)


# Lambda

def is_lambda(exp: ParsedExpression):
    return (
        is_list(exp) and
        len(exp) >= 3 and
        is_list(exp[1]) and
        exp[0] == "lambda" and
        all(isinstance(s, str) for s in exp[1])
    )