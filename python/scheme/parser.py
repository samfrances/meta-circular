from __future__ import annotations

from typing import Dict, Generator, List, Literal

from .common import ParsedExpression

OPENER_TO_CLOSER: Dict[str, Literal[")", "]", "}"]] = {
    "(": ")",
    "[": "]",
    "{": "}",
}


def tokenize(chars: str) -> Generator[TokenProcessor, None, None]:
    STRING_TOKENS = (
        chars.replace("(", " ( ")
        .replace(")", " ) ")
        .replace("[", " [ ")
        .replace("]", " ] ")
        .replace("{", " { ")
        .replace("}", " } ")
        .split()
    )

    OPENERS = tuple(OPENER_TO_CLOSER.keys())
    CLOSERS = tuple(OPENER_TO_CLOSER.values())

    for s_token in STRING_TOKENS:
        if s_token in OPENERS:
            yield OpenParen(s_token)
        elif s_token in CLOSERS:
            yield CloseParen(s_token)
        else:
            yield Atom(s_token)


class ListExpression:

    def __init__(self, opening_paren: str):
        """
        Create a ListExpression for the parser stack,
        specifying the symbol used to close that list
        expression
        """
        self._closer = OPENER_TO_CLOSER[opening_paren]
        self._items: List[TokenProcessor] = []

    def append(self, item: TokenProcessor):
        self._items.append(item)

    def __getitem__(self, key):
        return self._items[key]

    @property
    def closer(self):
        return self._closer

    def to_tuple(self):
        return tuple(self._items[:])


class TokenProcessor:
    """
    Base class, subclasses of which are specialised to parse a particular
    sort of token
    """

    def process(self, stack, result):
        raise NotImplementedError()


class OpenParen(TokenProcessor):

    def __init__(self, token):
        self._token = token

    def process(self, stack, result):
        stack.append(ListExpression(self._token))


class CloseParen(TokenProcessor):

    def __init__(self, token: str):
        self._closer = token

    def process(self, stack, result):
        if not stack:
            raise SyntaxError("Unmatched )")
        top = stack.pop()
        if top.closer != self._closer:
            raise SyntaxError(f"Expected closing '{top.closer}'")
        if stack:
            # Add completed list to previous list in stack
            stack[-1].append(top.to_tuple())
        else:
            # Add completed expression to result
            result.append(top.to_tuple())


class Atom(TokenProcessor):

    def __init__(self, token: str):
        self._token = token

    def process(self, stack, result):
        if not stack:
            result.append(self._typed_atom())
        else:
            top = stack[-1]
            top.append(self._typed_atom())

    def _typed_atom(self):

        if self._token == "#true":
            return True

        if self._token == "#false":
            return False

        try:
            return int(self._token)
        except ValueError:
            pass

        try:
            return float(self._token)
        except ValueError:
            pass

        return self._token


def read(tokens: Generator[TokenProcessor, None, None]):

    result: List[ParsedExpression] = []
    stack: List[ListExpression] = []

    tokens = list(tokens)

    for token in tokens:
        token.process(stack, result)

    if stack:
        raise MissingClosingParenError("Missing expected )")

    return result


class MissingClosingParenError(SyntaxError):
    pass


def parse(s: str):
    return read(tokenize(s))


# References:
# https://www.norvig.com/lispy.html
# https://www.freecodecamp.org/news/s-expressions-in-javascript/
