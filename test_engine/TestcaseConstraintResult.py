"""
See COPYRIGHT.md for copyright information.
"""
from __future__ import annotations
from dataclasses import dataclass

from arelle.ModelValue import QName
from test_engine.ErrorLevel import ErrorLevel


@dataclass(frozen=True)
class TestcaseConstraintResult:
    code: tuple[str | QName | None, ErrorLevel]
    diff: int

    def __str__(self) -> str:
        if self.diff == 0:
            message = 'Matched'
        elif self.diff < 0:
            message = f'Missing {abs(self.diff)} expected'
        else:
            message = f'{self.diff} unexpected'
        code, level = self.code
        return f"{message} {level} \"{code or '(any)'}\""  # TODO: `code` is ending up as the string "None"
