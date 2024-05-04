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


def test_flat_environment_set_after_define():
    env = Environment()
    key = "foo"
    value = 43
    later_value = 88
    env.define(key, value)
    env[key] = later_value

    assert env[key] == later_value