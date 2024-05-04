# scheme.py
#
# Challenge: Can you implement a scheme interpreter in Python that's
# capable of executing the following procedure?

# A procedure definition for:
#
#   (define fact
#      (lambda (n) (if (= n 1)
#                   1
#                   (* n (fact (- n 1))))))
#
# It's represented in Python using the following tuple:

fact = (
    "define",
    "fact",
    ("lambda", ("n",), ("if", ("=", "n", 1), 1, ("*", "n", ("fact", ("-", "n", 1))))),
)


env = {
    "+": lambda x, y: x + y,
    "*": lambda x, y: x * y,
    "-": lambda x, y: x - y,
    "=": lambda x, y: x == y,
}


def env_lookup(sym):
    return env[sym]


def substitute(sexp, name, value):
    if isinstance(sexp, str) and sexp == name:
        return value
    elif isinstance(sexp, tuple):
        return tuple(substitute(item, name, value) for item in sexp)
    else:
        return sexp


# You will define the following procedure for evaluating an expression
def seval(sexp):
    if isinstance(sexp, int):  # Primitive
        return sexp
    if isinstance(sexp, bool):
        return sexp
    elif isinstance(sexp, str):  # Symbol
        return env_lookup(sexp)
    elif isinstance(sexp, tuple):  # Function application
        if sexp[0] == "define":
            name = sexp[1]
            value = seval(sexp[2])
            env[name] = value
            return

        if sexp[0] == "if":
            the_test = sexp[1]
            testeval = seval(the_test)
            branch = sexp[2] if testeval else sexp[3]
            return seval(branch)

        if sexp[0] == "lambda":
            argnames = sexp[1]
            body = sexp[2]

            def procedure(*args):
                evaluated_body = body
                for argname, argvalue in zip(argnames, args):
                    evaluated_body = substitute(evaluated_body, argname, argvalue)
                return seval(evaluated_body)

            return procedure

        proc = sexp[0]
        args = sexp[1:]
        evaluated_proc = seval(proc)
        evaluated_args = [seval(arg) for arg in args]
        return evaluated_proc(*evaluated_args)
    else:
        raise RuntimeError("You wot mate?")


# In writing seval, you are ONLY allowed to use the rules of Scheme
# evaluation that you currently know about.  So far, this includes the
# substitution model and the notion of special forms.

# Some basic tests
assert seval(42) == 42
assert seval(("+", 2, 3)) == 5
assert seval(("-", 2, 3)) == -1
assert seval(("=", ("+", 2, 3), ("-", 6, 1)))
seval(("define", "n", 5))
assert seval("n") == 5
seval(("define", "p", ("+", 1, 1)))
assert seval("p") == 2
assert seval(("if", ("=", "p", 2), 100, 200)) == 100
assert seval(("if", ("=", "p", 3), 100, 200)) == 200

code = ("lambda", ("x",), ("+", "x", 1))

# Now the ultimate test--can you run your procedure?
f = seval(code)
print(f(5))

seval(fact)
print(seval(("fact", "n")))
assert seval(("fact", "n")) == 120

# Are variables scoped?
seval(("define", "x", 3))

code = ("define", "foo", ("lambda", (), ("define", "x", 4)))
seval(code)

assert seval("x") == 3

seval(("foo",))

assert seval("x") == 4
