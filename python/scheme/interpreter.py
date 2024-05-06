from __future__ import annotations

import operator
from typing import Any, Dict, Literal, Tuple, Optional, TypeGuard

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
        except KeyError:
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
    env.define("and", operator.and_)
    env.define("or", operator.or_)
    env.define("not", operator.not_)
    env.define("display", lambda x: print(x))
    return env


def seval(exp: ParsedExpression, env: Environment):
    if is_primitive(exp):
        return exp
    if is_symbol(exp):
        return env[exp]
    if is_if(exp):
        return seval_if_statement(exp, env)
    if is_let(exp):
        return seval_let(exp, env)
    if is_define_exp(exp):
        return seval_define(exp, env)
    if is_proc_define(exp):
        return seval_proc_define(exp, env)
    if is_lambda(exp):
        return seval_lambda(exp, env)
    if is_list(exp):
        func_name_or_expr = exp[0]
        func_args = exp[1:]
        return sapply(func_name_or_expr, func_args, env)


def sapply(
    proc_name: ParsedExpression, proc_args: ParsedExpressionList, env: Environment
):
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
    return (
        is_list(exp)
        and len(exp) == 3
        and exp[0] == "define"
        and isinstance(exp[1], str)
    )


def seval_define(exp: VariableDefinition, env: Environment):
    name = exp[1]
    definition = exp[2]
    value = seval(definition, env)
    env.define(name, value)


# Lambda

ProcHeader = Tuple[str, ...]
LambdaExpression = Tuple[Literal["lambda"], ProcHeader, ParsedExpression]


def is_lambda(exp: ParsedExpression) -> TypeGuard[LambdaExpression]:
    return (
        is_list(exp) and len(exp) == 3 and exp[0] == "lambda" and is_proc_header(exp[1])
    )


def is_proc_header(exp: ParsedExpression) -> TypeGuard[ProcHeader]:
    return is_list(exp) and all(isinstance(s, str) for s in exp)


def seval_lambda(exp: LambdaExpression, env: Environment):
    header, body = exp[1:]
    return make_lambda(header, body, env)


def make_lambda(header: ProcHeader, body: ParsedExpression, env: Environment):

    def proc(*args):
        localenv = Environment(env)
        for var_name, val in zip(header, args):
            print(var_name, val)
            localenv.define(var_name, val)
        if len(args) != len(header):
            raise Exception(f"Arity error, expected {len(header)}, got {len(args)}")
        return seval(body, localenv)

    return proc


# Function definition syntactic_sugar

DefineProcExpression = Tuple[Literal["define"], str, ProcHeader, ParsedExpression]


def is_proc_define(exp: ParsedExpression) -> TypeGuard[DefineProcExpression]:
    return (
        is_list(exp)
        and len(exp) == 4
        and exp[0] == "define"
        and isinstance(exp[1], str)
        and is_proc_header(exp[2])
    )


def seval_proc_define(exp: DefineProcExpression, env: Environment):
    """
    Evaluate function define syntactic sugar by transforming into
    the equivalent that uses a lambda expression before evaluating
    """
    proc_name = exp[1]
    header = exp[2]
    body = exp[3]
    equivalent_lambda: ParsedExpression = ("lambda", header, body)
    equivalent_define: VariableDefinition = ("define", proc_name, equivalent_lambda)
    return seval_define(equivalent_define, env)


# if statement

IfStatement = Tuple[Literal["if"], ParsedExpression, ParsedExpression, ParsedExpression]


def is_if(exp: ParsedExpression) -> TypeGuard[IfStatement]:
    return is_list(exp) and len(exp) == 4 and exp[0] == "if"


def seval_if_statement(exp: IfStatement, env: Environment):
    test = exp[1]
    true_branch = exp[2]
    false_branch = exp[3]

    if seval(test, env):
        return seval(true_branch, env)
    else:
        return seval(false_branch, env)


# Let statement

LetAssignment = Tuple[str, ParsedExpression]
LetStatement = Tuple[Literal["let"], Tuple[LetAssignment, ...], ParsedExpression]


def is_let(exp: ParsedExpression) -> TypeGuard[LetStatement]:
    if not (is_list(exp) and len(exp) == 3 and exp[0] == "let"):
        return False

    assignments = exp[1]
    if not is_list(assignments):
        return False

    for assignment in assignments:
        if not is_list(assignment):
            return False
        if len(assignment) != 2:
            return False
        if not isinstance(assignment[0], str):
            return False

    return True


def seval_let(exp: LetStatement, env: Environment):
    assigments = exp[1]
    body = exp[2]

    localenv = Environment(env)

    for assignment in assigments:
        name = assignment[0]
        value_expr = assignment[1]
        value = seval(value_expr, localenv)
        localenv.define(name, value)

    return seval(body, localenv)
