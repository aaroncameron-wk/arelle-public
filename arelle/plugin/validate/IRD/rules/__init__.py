"""
See COPYRIGHT.md for copyright information.

Shared helpers for IRD validation rules.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
from typing import TYPE_CHECKING

from arelle.ModelValue import QName
from arelle.utils.validate.Facts import iterValidNonNilFactsByQname

if TYPE_CHECKING:
    from arelle.ModelInstanceObject import ModelFact
    from arelle.ModelXbrl import ModelXbrl


def getFactsByDateValue(modelXbrl: ModelXbrl, qnames: tuple[QName, ...]) -> dict[date, list[ModelFact]]:
    factsByValue = defaultdict(list)
    for qname in qnames:
        for fact in iterValidNonNilFactsByQname(modelXbrl, qname):
            if isinstance(fact.xValue, datetime):
                factsByValue[fact.xValue.date()].append(fact)
    return dict(factsByValue)
