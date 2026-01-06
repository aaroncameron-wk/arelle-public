"""
See COPYRIGHT.md for copyright information.
"""
from __future__ import annotations

from dataclasses import dataclass

from arelle.ModelValue import QName
from test_engine.ErrorLevel import ErrorLevel


@dataclass(frozen=True)
class TestcaseConstraint:
    qname: QName | None = None
    pattern: str | None = None
    count: int = 1
    level: ErrorLevel = ErrorLevel.ERROR

    def __str__(self) -> str:
        value = str(self.qname or self.pattern or '(any)')
        if self.level:
            value += f" [{self.level}]"
        if self.count != 1:
            value += f" x{self.count}"
        return value
