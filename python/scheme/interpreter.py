from __future__ import annotations

import operator
from typing import Any, Dict, Tuple, Optional, TypeGuard

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
    env.define("newline", lambda: print())
    return env


def seval(exp: ParsedExpression, env: Environment):
    ORDER_OF_EXPRESSION_TYPES = (
        Primitive.from_parsed_expression,  # Not preferred, but needed for mypy
        Symbol.from_parsed_expression,
        IfStatement.from_parsed_expression,
        LetStatement.from_parsed_expression,
        BeginExpression.from_parsed_expression,
        VariableDefinition.from_parsed_expression,
        DefineProcExpression.from_parsed_expression,
        LambdaExpression.from_parsed_expression,
        ProcApplication.from_parsed_expression,
    )

    for exp_type in ORDER_OF_EXPRESSION_TYPES:
        exp_for_evaluation = exp_type(exp)
        if exp_for_evaluation is not None:
            return exp_for_evaluation.seval(env)
    else:
        raise Exception("Bad expression")


def sapply(
    proc_name: ParsedExpression, proc_args: ParsedExpressionList, env: Environment
):
    proc = seval(proc_name, env)
    if not callable(proc):
        raise Exception("Invalid function application")
    args = [seval(a, env) for a in proc_args]
    return proc(*args)


def is_list(exp: ParsedExpression) -> TypeGuard[ParsedExpressionList]:
    return isinstance(exp, tuple)


# procedure application


class ProcApplication:

    _proc_name_or_expr: ParsedExpression
    _proc_args: ParsedExpressionList

    def __init__(
        self, proc_name_or_expr: ParsedExpression, proc_args: ParsedExpressionList
    ):
        self._proc_name_or_expr = proc_name_or_expr
        self._proc_args = proc_args

    @classmethod
    def from_parsed_expression(cls, exp: ParsedExpression) -> Optional[ProcApplication]:
        if not is_list(exp):
            return None

        proc_name_or_expr = exp[0]
        proc_args: ParsedExpressionList = exp[1:]

        return cls(proc_name_or_expr, proc_args)

    def seval(self, env: Environment):
        return sapply(self._proc_name_or_expr, self._proc_args, env)


# primitive


class Primitive:

    _value: float | int | bool

    def __init__(self, value: float | int | bool):
        self._value = value

    @classmethod
    def from_parsed_expression(cls, exp: ParsedExpression) -> Optional[Primitive]:
        if not (
            isinstance(exp, float) or isinstance(exp, int) or isinstance(exp, bool)
        ):
            return None

        return cls(exp)

    def seval(self, _env: Environment):
        return self._value


# Symbol


class Symbol:

    _name: str

    def __init__(self, name: str):
        self._name = name

    @classmethod
    def from_parsed_expression(cls, exp: ParsedExpression) -> Optional[Symbol]:
        if not isinstance(exp, str):
            return None

        return cls(exp)

    def seval(self, env: Environment):
        return env[self._name]


# Define


class VariableDefinition:

    _name: str
    _definition: ParsedExpression

    def __init__(self, name: str, definition: ParsedExpression):
        self._name = name
        self._definition = definition

    @classmethod
    def from_parsed_expression(
        cls, exp: ParsedExpression
    ) -> Optional[VariableDefinition]:
        if not (is_list(exp) and len(exp) == 3 and exp[0] == "define"):
            return None

        name = exp[1]
        if not isinstance(name, str):
            return None

        definition = exp[2]

        return cls(name, definition)

    def seval(self, env: Environment):
        value = seval(self._definition, env)
        env.define(self._name, value)


# Lambda

ProcHeader = Tuple[str, ...]


def is_proc_header(exp: ParsedExpression) -> TypeGuard[ProcHeader]:
    return is_list(exp) and all(isinstance(s, str) for s in exp)


class LambdaExpression:

    _header: ProcHeader
    _body: ParsedExpression

    def __init__(self, header: ProcHeader, body: ParsedExpression):
        self._header = header
        self._body = body

    @classmethod
    def from_parsed_expression(
        cls, exp: ParsedExpression
    ) -> Optional[LambdaExpression]:
        if not (is_list(exp) and len(exp) == 3 and exp[0] == "lambda"):
            return None

        header = exp[1]

        if not is_proc_header(header):
            return None

        body = exp[2]

        return cls(header, body)

    def seval(self, env: Environment):
        header = self._header
        body = self._body

        def proc(*args):
            localenv = Environment(env)
            for var_name, val in zip(header, args):
                localenv.define(var_name, val)
            if len(args) != len(header):
                raise Exception(f"Arity error, expected {len(header)}, got {len(args)}")
            return seval(body, localenv)

        return proc


# Function definition syntactic_sugar


class DefineProcExpression:

    _name: str
    _header: ProcHeader
    _body: ParsedExpression

    def __init__(self, name: str, header: ProcHeader, body: ParsedExpression):
        self._name = name
        self._header = header
        self._body = body

    @classmethod
    def from_parsed_expression(
        cls, exp: ParsedExpression
    ) -> Optional[DefineProcExpression]:
        if not (is_list(exp) and len(exp) == 4 and exp[0] == "define"):
            return None

        name = exp[1]
        if not isinstance(name, str):
            return None

        header = exp[2]
        if not is_proc_header(header):
            return None

        body = exp[3]

        return cls(name, header, body)

    def seval(self, env: Environment):
        """
        Evaluate function define syntactic sugar by transforming into
        the equivalent that uses a lambda expression before evaluating
        """
        equivalent_lambda: ParsedExpression = ("lambda", self._header, self._body)
        equivalent_define = VariableDefinition(self._name, equivalent_lambda)
        return equivalent_define.seval(env)


# If statement


class IfStatement:

    _test: ParsedExpression
    _true_branch: ParsedExpression
    _false_branch: ParsedExpression

    def __init__(
        self,
        test: ParsedExpression,
        true_branch: ParsedExpression,
        false_branch: ParsedExpression,
    ):
        self._test = test
        self._true_branch = true_branch
        self._false_branch = false_branch

    @classmethod
    def from_parsed_expression(cls, exp: ParsedExpression) -> Optional[IfStatement]:
        if not (is_list(exp) and len(exp) == 4 and exp[0] == "if"):
            return None

        test = exp[1]
        true_branch = exp[2]
        false_branch = exp[3]

        return cls(test, true_branch, false_branch)

    def seval(self, env: Environment):
        if seval(self._test, env):
            return seval(self._true_branch, env)
        else:
            return seval(self._false_branch, env)


# Let statement

LetAssignment = Tuple[str, ParsedExpression]


def is_let_assignment(exp: ParsedExpression) -> TypeGuard[LetAssignment]:
    if not is_list(exp):
        return False
    if len(exp) != 2:
        return False
    if not isinstance(exp[0], str):
        return False
    return True


class LetStatement:

    _assignments: Tuple[LetAssignment, ...]
    _body: ParsedExpression

    def __init__(self, assignments: Tuple[LetAssignment, ...], body: ParsedExpression):
        self._assignments = assignments
        self._body = body

    @classmethod
    def from_parsed_expression(cls, exp: ParsedExpression) -> Optional[LetStatement]:
        if not (is_list(exp) and len(exp) == 3 and exp[0] == "let"):
            return None

        assignments = exp[1]
        if not is_list(assignments):
            return None

        typed_assignments: list[LetAssignment] = []
        for assignment in assignments:
            if is_let_assignment(assignment):
                typed_assignments.append(assignment)
            else:
                return None

        body = exp[2]

        return cls(tuple(typed_assignments), body)

    def seval(self, env: Environment):
        assigments = self._assignments
        body = self._body

        localenv = Environment(env)

        for assignment in assigments:
            name = assignment[0]
            value_expr = assignment[1]
            value = seval(value_expr, localenv)
            localenv.define(name, value)

        return seval(body, localenv)


# Begin expression


class BeginExpression:

    _statements: ParsedExpressionList

    def __init__(self, statements: ParsedExpressionList):
        self._statements = statements

    @classmethod
    def from_parsed_expression(cls, exp: ParsedExpression):
        if not (is_list(exp) and len(exp) >= 2 and exp[0] == "begin"):
            return

        return cls(exp[1:])

    def seval(self, env: Environment):
        result = None
        for exp in self._statements:
            result = seval(exp, env)
        return result
