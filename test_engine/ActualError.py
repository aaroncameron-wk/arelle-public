"""
See COPYRIGHT.md for copyright information.
"""
from __future__ import annotations

from dataclasses import dataclass

from arelle.ModelValue import QName
from test_engine.ErrorLevel import ErrorLevel


@dataclass(frozen=True)
class ActualError:
    code: str | None
    qname: QName | None
    level: ErrorLevel

    def __str__(self) -> str:
        value = str(self.qname or self.code)
        if self.level:
            value += f" [{self.level}]"
        return value
