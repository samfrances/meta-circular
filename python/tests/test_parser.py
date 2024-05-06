import pytest

from scheme.parser import parse


@pytest.mark.parametrize(
    "input,parsed",
    (
        (
            "",
            [],
        ),
        ("()", [()]),
        ("[]", [()]),
        ("{}", [()]),
        ("() ()", [(), ()]),
        ("[] []", [(), ()]),
        ("{} {}", [(), ()]),
        ("[] ()", [(), ()]),
        ("() []", [(), ()]),
        ("{} ()", [(), ()]),
        ("() () ()", [(), (), ()]),
        ("()\n()", [(), ()]),
        ("(a)", [("a",)]),
        ("(a) (b) () (c)", [("a",), ("b",), (), ("c",)]),
        ("(a b)", [("a", "b")]),
        ("(a b c)", [("a", "b", "c")]),
        ("(a b (c d))", [("a", "b", ("c", "d"))]),
        ("(a b (c d)) (a)", [("a", "b", ("c", "d")), ("a",)]),
        ("(1)", [(1,)]),
        ("(1.2)", [(1.2,)]),
        ("a", ["a"]),
        ("a (foo 1 2) b", ["a", ("foo", 1, 2), "b"]),
        ("1", [1]),
        ("#true", [True]),
        ("#false", [False]),
        ("(#true b (c #false))", [(True, "b", ("c", False))]),
    ),
)
def test_parser_on_valid_inputs(input, parsed):
    assert parse(input) == parsed


MISSING_EXPECTED = "Missing expected"
UNMATCHED = "Unmatched"


@pytest.mark.parametrize(
    "input, error_message",
    (
        ("(", MISSING_EXPECTED),
        (")", UNMATCHED),
        ("(a b c))", UNMATCHED),
        ("((a b c)", MISSING_EXPECTED),
        ("[", MISSING_EXPECTED),
        ("]", UNMATCHED),
        ("[a b c]]", UNMATCHED),
        ("[[a b c]", MISSING_EXPECTED),
        ("[a b c}", "Expected closing"),
    ),
)
def test_parser_on_mismatched_parens(input, error_message):
    with pytest.raises(SyntaxError) as e:
        parse(input)
    assert error_message in str(e.value)
