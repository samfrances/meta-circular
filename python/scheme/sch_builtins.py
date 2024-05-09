from operator import add, mul, truediv, and_, or_, not_
from typing import Any, Optional  # noqa

def display(value: Any):
    print(value)

def newline():
    print()

def minus(x: int|float, y: Optional[int] = None):
    if y is None:
        return -x
    return x - y
