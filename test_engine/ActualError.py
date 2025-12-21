"""
See COPYRIGHT.md for copyright information.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

from arelle.ModelValue import QName

class ErrorLevel(Enum):
    OK = "OK"
    SATISIFED = "SATISIFED"
    NOT_SATISFIED = "NOT_SATISFIED"
    WARNING = "WARNING"
    ERROR = "ERROR"

    def __str__(self):
        return self.value

@dataclass(frozen=True)
class ActualError:
    code: str | None
    qname: QName | None
    level: ErrorLevel

    def __str__(self):
        value = str(self.qname or self.code)
        if self.level:
            value += f" [{self.level}]"
        return value
