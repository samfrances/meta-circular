import pytest

from ..interpreter import Environment

def test_flat_environment_miss():

    env = Environment()
    with pytest.raises(KeyError):
        env["foo"]

def test_flat_environment_hit():

    env = Environment()
    key = "foo"
    value = 43
    env.define(key, value)
    assert env[key] == value


def test_flat_environment_set_before_define():

    env = Environment()
    key = "bar"
    value = 578
    with pytest.raises(KeyError):
        env[key] = value


def test_define_twice():

    env = Environment()
    key = "bar"
    env.define(key, 1)
    with pytest.raises(Exception):
        env.define(key, 2)


def test_flat_environment_set_after_define():
    env = Environment()
    key = "foo"
    value = 43
    later_value = 88
    env.define(key, value)
    env[key] = later_value

    assert env[key] == later_value


def test_nested_environment_miss():

    enclosing = Environment()
    env = Environment(enclosing)

    with pytest.raises(KeyError):
        env["baz"]


def test_nested_environment_hit():

    enclosing = Environment()
    key = "foo"
    value = 100
    enclosing.define(key, value)

    env = Environment(enclosing)

    assert env[key] == value


def test_nested_and_flat_hits():

    enclosing = Environment()
    key = "foo"
    value = 100
    enclosing.define(key, value)

    env = Environment(enclosing)
    second_key = "beef"
    second_value = 1111
    env.define(second_key, second_value)

    assert env[key] == value
    assert env[second_key] == second_value


def test_more_realistic_example():

    global_env = Environment()

    middle_env = Environment(global_env)

    env = Environment(middle_env)

    global_contents = {
        "foo": 1,
        "bar": 99,
        "incr": lambda x: x+1
    }

    middle_contents = {
        "baz": 99,
        "add": lambda x, y: x + y
    }

    env_contents = {
        "one": 2
    }

    for key, val in global_contents.items():
        global_env.define(key, val)

    for key, val in middle_contents.items():
        middle_env.define(key, val)

    for key, val in env_contents.items():
        env.define(key, val)

    with pytest.raises(KeyError):
        env["not_here"]

    for key in env_contents:
        assert env[key] == env_contents[key]

    for key in middle_contents:
        assert env[key] == middle_contents[key]

    for key in global_contents:
        assert env[key] == global_contents[key]
