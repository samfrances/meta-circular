from __future__ import annotations

from typing import Optional

class Environment:

    def __init__(self, enclosing: Optional[Environment] = None):
        self._enclosing = enclosing
        self._table = {}

    def __getitem__(self, key: str):
        return self._table[key]

    def __setitem__(self, key: str, value):
        if key not in self._table:
            raise KeyError(key)
        self._table[key] = value

    def define(self, key: str, value):
        self._table[key] = value