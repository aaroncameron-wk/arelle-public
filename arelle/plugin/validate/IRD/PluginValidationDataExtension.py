"""
See COPYRIGHT.md for copyright information.
"""
from __future__ import annotations

from dataclasses import dataclass

from arelle.ModelValue import QName
from arelle.utils.PluginData import PluginData


@dataclass
class PluginValidationDataExtension(PluginData):

    # ── Accounting period (nvad_accounting_period) ───────────────────────
    accountingDateDifferentQn: QName
    reasonsForChangeOfAccountingDateQn: QName
    accountingPeriodStartDateQn: QName
    accountingPeriodEndDateQn: QName

    # Identity hash for caching.
    def __hash__(self) -> int:
        return id(self)
