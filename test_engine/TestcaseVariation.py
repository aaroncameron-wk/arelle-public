"""
See COPYRIGHT.md for copyright information.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

from test_engine.ErrorLevel import ErrorLevel
from test_engine.TestcaseConstraintSet import TestcaseConstraintSet


@dataclass(frozen=True)
class TestcaseVariation:
    id: str
    fullId: str
    name: str
    description: str
    base: str
    readFirstUris: list[str]
    shortName: str
    status: str
    testcaseConstraintSet: TestcaseConstraintSet
    blockedCodePattern: str
    calcMode: str | None
    parameters: str
    ignoreLevels: frozenset[ErrorLevel]
    compareFormulaOutputUri: Path | None
    compareInstanceUri: Path | None
    inlineTarget: str | None
