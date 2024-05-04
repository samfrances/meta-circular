from __future__ import annotations

from typing import Generator, List, Union


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

    OPENERS = ("(", "[", "{")

    CLOSERS = (")", "]", "}")

    OPENER_TO_CLOSER = dict(zip(OPENERS, CLOSERS))

    for s_token in STRING_TOKENS:
        if s_token in OPENERS:
            yield OpenParen(OPENER_TO_CLOSER[s_token])
        elif s_token in CLOSERS:
            yield CloseParen(s_token)
        else:
            yield Atom(s_token)


class ListExpression:

    def __init__(self, closer: str):
        self._closer = closer
        self._items: List[TokenProcessor] = []

    def append(self, item: TokenProcessor):
        self._items.append(item)

    def __getitem__(self, key):
        return self._items[key]

    @property
    def closer(self):
        return self._closer

    def to_list(self):
        return self._items[:]


class TokenProcessor:

    def process(self, stack, result):
        pass


class OpenParen(TokenProcessor):

    def __init__(self, paren_type: str):
        self._paren_type = paren_type

    def process(self, stack, result):
        stack.append(ListExpression(self._paren_type))


class CloseParen(TokenProcessor):

    def __init__(self, closer: str):
        self._closer = closer

    def process(self, stack, result):
        if not stack:
            raise SyntaxError("Unmatched )")
        top = stack.pop()
        if top.closer != self._closer:
            print(top.closer, self._closer)
            raise SyntaxError(f"Expected closing '{top.closer}'")
        if stack:
            # Add completed list to previous list in stack
            stack[-1].append(top.to_list())
        else:
            # Add completed expression to result
            result.append(top.to_list())


class Atom(TokenProcessor):

    def __init__(self, token: str):
        self._token = token

    def process(self, stack, result):
        top = stack[-1]
        top.append(self._typed_atom())

    def _typed_atom(self):
        try:
            return int(self._token)
        except ValueError:
            pass

        try:
            return float(self._token)
        except ValueError:
            pass

        return self._token


ParsedExpression = List[Union[float, int, str, "ParsedExpression"]]


def read(tokens: Generator[TokenProcessor, None, None]):

    result: List[ParsedExpression] = []
    stack: List[ListExpression] = []

    for token in tokens:
        token.process(stack, result)

    if stack:
        raise SyntaxError("Missing expected )")

    return result


def parse(s: str):
    return read(tokenize(s))


# References:
# https://www.norvig.com/lispy.html
# https://www.freecodecamp.org/news/s-expressions-in-javascript/
