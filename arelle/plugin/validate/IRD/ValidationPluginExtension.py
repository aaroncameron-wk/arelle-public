"""
See COPYRIGHT.md for copyright information.
"""
from __future__ import annotations

from arelle.Cntlr import Cntlr
from arelle.ModelValue import QName, qname
from arelle.utils.validate.ValidationPlugin import ValidationPlugin
from arelle.ValidateXbrl import ValidateXbrl

from .PluginValidationDataExtension import PluginValidationDataExtension

TC_NAMESPACE = "http://xbrl.ird.gov.hk/taxonomy/2026-04-01/ird_tc"


def tcQn(local: str) -> QName:
    return qname(f"{{{TC_NAMESPACE}}}{local}")


class ValidationPluginExtension(ValidationPlugin):
    def newPluginData(
        self,
        cntlr: Cntlr,
        validateXbrl: ValidateXbrl | None,
    ) -> PluginValidationDataExtension:
        return PluginValidationDataExtension(
            name=self.name,

            # accounting period
            accountingDateDifferentQn=tcQn("AccountingDateDifferentFromThatOfLastYear"),
            reasonsForChangeOfAccountingDateQn=tcQn("ReasonsForTheChangeOfAccountingDate"),
            accountingPeriodStartDateQn=tcQn("AccountingPeriodStartDate"),
            accountingPeriodEndDateQn=tcQn("AccountingPeriodEndDate"),
        )
