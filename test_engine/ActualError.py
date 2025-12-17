"""
See COPYRIGHT.md for copyright information.
"""
from __future__ import annotations
from dataclasses import dataclass

from arelle.ModelValue import QName


@dataclass(frozen=True)
class ActualError:
    code: str
    qname: QName | None
