"""
See COPYRIGHT.md for copyright information.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache

from arelle.ModelDocumentType import ModelDocumentType
from arelle.ModelInstanceObject import ModelFact
from arelle.ModelObject import ModelObject
from arelle.ModelValue import QName
from arelle.ModelXbrl import ModelXbrl
from arelle.utils.PluginData import PluginData
from arelle.utils.validate.Facts import isValidNonNilFact, hasValidNonNilFactByQname

LINKBASE_NS = "http://www.xbrl.org/2003/linkbase"
XLINK_HREF = "{http://www.w3.org/1999/xlink}href"
SCHEMA_REF_TAG = f"{{{LINKBASE_NS}}}schemaRef"


@dataclass
class PluginValidationDataExtension(PluginData):

    # Namespace constants
    tcNamespace: str   # "http://xbrl.ird.gov.hk/taxonomy/2026-04-01/ird_tc"
    fsNamespace: str   # "http://xbrl.ird.gov.hk/taxonomy/2026-04-01/ird_fs"
    fspeNamespace: str  # "http://xbrl.ird.gov.hk/taxonomy/2026-04-01/ird_fs_pe"

    # Taxonomy entry point URIs (553-E rules)
    validTcEntryPoints: frozenset[str]
    validFsEntryPoints: frozenset[str]
    validFsPeEntryPoints: frozenset[str]

    assessmentYear: int

    # Mandatory element sets (NVAD-E-0010, NVAD-E-0050)
    mandatoryTcBir51Qns: frozenset[QName]
    mandatoryTcBir52Qns: frozenset[QName]

    # Form-type detection
    # NVAD-E-0060: these concepts must NOT appear in a BIR51 (corporation) filing.
    bir52ExclusiveQns: frozenset[QName]
    # NVAD-E-0070: these concepts must NOT appear in a BIR52 (partnership) filing.
    bir51ExclusiveQns: frozenset[QName]

    # Identifiers & basis period
    companyNameQn: QName
    irdFileNumberQn: QName
    yearOfAssessmentQn: QName
    basisPeriodStartDateQn: QName
    basisPeriodEndDateQn: QName

    # Accounting period (nvad_accounting_period)
    accountingDateDifferentQn: QName      # AccountingDateDifferentFromThatOfLastYear
    reasonsForChangeOfAccountingDateQn: QName  # ReasonsForTheChangeOfAccountingDate
    accountingPeriodStartDateQn: QName
    accountingPeriodEndDateQn: QName

    # Currency / conversion (nvad_currency)
    currencyUsedQn: QName
    conversionRateQn: QName
    # AssessableProfitsAdjustedLossOfThePeriodHKD (NVAD-E-1170, 1180)
    assessableProfitsQn: QName

    # Income paired (nvad_income_paired)
    serviceFeeIncomeQn: QName             # ServiceFeeIncome
    serviceFeeReceivedDetailsQn: QName    # ServiceFeeReceivedDetails
    managementFeeIncomeQn: QName          # ManagementFeeIncome
    managementFeeReceivedDetailsQn: QName  # ManagementFeeReceivedDetails
    offshoreProfitsExcludedQn: QName      # OffshoreProfitsExcluded
    reasonsForOffshoreClaimQn: QName      # ReasonsForTheOffshoreClaim

    # Expense deductions (nvad_expense_deductions)
    commissionQn: QName                              # Commission
    commissionPaymentsDetailsQn: QName               # CommissionPaymentsDetails
    approvedCharitableDonationsTaxAdjQn: QName       # ApprovedCharitableDonationsTaxAdjustment
    approvedCharitableDonationsDetailsQn: QName      # ApprovedCharitableDonationsDetails
    interestExpensesQn: QName                        # InterestExpenses
    interestPaidOrPayableDetailsQn: QName            # InterestPaidOrPayableDetails
    legalAndProfessionalFeeQn: QName                 # LegalAndProfessionalFee
    legalAndProfessionalFeeDetailsQn: QName          # LegalAndOtherProfessionalFeePaymentsDetails

    # Expense misc (nvad_expense_misc)
    managementFeeQn: QName                           # ManagementFee (expense)
    managementFeePaymentsDetailsQn: QName            # ManagementFeePaymentsDetails
    contractorChargesQn: QName                       # ContractorCharges
    subContractorChargesQn: QName                    # SubContractorCharges
    contractorAndSubcontractorChargesDetailsQn: QName
    provisionSpecificBadDebtQn: QName                # ProvisionSpecificBadDebt
    badDebtProvisionDetailsQn: QName                 # BadDebtProvisionDetails

    # BIR51 share-based payments (nvad_bir51_sbp)
    shareBasedPaymentDetailsQn: QName
    shareBasedPaymentCashSettledQn: QName            # ShareBasedPaymentCashSettled
    shareBasedPaymentEquitySettledCompanyQn: QName   # ShareBasedPaymentEquitySettledCompany
    shareBasedPaymentEquitySettledGroupNoRechargeQn: QName  # ShareBasedPaymentEquitySettledGroupCoNoRecharge
    shareBasedPaymentEquitySettledGroupRechargeQn: QName    # ShareBasedPaymentEquitySettledGroupCoRecharge

    # Environmental (nvad_environmental)
    buildingRefurbTaxAdjQn: QName      # ExpenditureOnBuildingRefurbishmentTaxAdjustment
    buildingRefurbDetailsQn: QName     # ExpenditureOnBuildingRefurbishmentDetails
    epMachineryTaxAdjQn: QName         # ExpenditureOnEnvironmentalProtectionMachineryTaxAdjustment
    epMachineryDetailsQn: QName        # DetailsOfExpenditureIncurredOnAndProceedsFromTheSaleOfEnvironmentalProtectionMachinery
    epInstallationTaxAdjQn: QName      # ExpenditureOnEnvironmentalProtectionInstallationTaxAdjustment
    epInstallationDetailsQn: QName     # DetailsOfExpenditureIncurredOnAndProceedsFromTheSaleOfEnvironmentalProtectionInstallation
    efVehiclesTaxAdjQn: QName          # ExpenditureOnEnvironmentFriendlyVehiclesTaxAdjustment
    efVehiclesDetailsQn: QName         # DetailsOfExpenditureIncurredOnAndProceedsFromTheSaleOfEnvironmentFriendlyVehicles

    # Special flags (nvad_special_flags)
    advanceRulingQn: QName             # AdvanceRuling
    advanceRulingDetailsQn: QName      # AdvanceRulingDetails
    permanentEstablishmentQn: QName    # PermanentEstablishmentHongKongNonHongKongResidentPerson
    transactionsWithOtherPartsQn: QName  # TransactionsWithOtherPartsNonHongKongResidentPerson
    practisingCertificateNumberQn: QName
    hongKongPracticeUnitQn: QName

    # Business lifecycle (nvad_lifecycle)
    businessCommencementQn: QName
    businessCommencementDateQn: QName
    businessCessationQn: QName
    businessCessationDateQn: QName
    businessCessationDeathOfProprietorQn: QName
    businessCessationProprietorDeathDateQn: QName
    businessCessationTransferredQn: QName
    businessCessationTransfereeQn: QName
    businessCessationTransfereeBusinessNatureQn: QName
    businessCessationTransferredAssetsAssociatedQn: QName  # BusinessCessationTransferredAssetsAssociated

    # BIR51 corporate flags (nvad_bir51_corporate)
    privateCompanyQn: QName
    shareholderChangeQn: QName
    insuranceRbcFlagQn: QName          # InsuranceCorporationCommencingToImplementRiskBasedCapitalRegimeToDetermineCapitalRequirements
    incomeRbcAmountQn: QName           # IncomeAmountOfOneOffAdjustmentArisingFromImplementationOfRBCRegime
    lossRbcAmountQn: QName             # LossAmountOfOneOffAdjustmentArisingFromImplementationOfRBCRegime
    electToTreatOneOffAdjustmentQn: QName  # ElectToTreatOneOffAdjustmentAsYourIncomeOrLossBy5EqualAmounts
    familyOwnedSpeQn: QName            # FamilyOwnedSpecialPurposeEntityInWhichAnEligibleFamilyOwnedInvestmentHoldingVehicleHasBeneficialInterest
    profitsEarnedByFamilyOwnedSpeQn: QName  # ProfitsEarnedByAFamilyOwnedSpecialPurposeEntityFromTransactionsSpecified

    # BIR52 partners (nvad_bir52_partners)
    bir52ProprietorPartnerEmolumentsQn: QName       # BIR52ProprietorPartnerEmoluments
    bir52ProprietorPartnerEmolumentsAdjQn: QName    # BIR52ProprietorPartnerEmolumentsAdjustment
    partnersDimensionQn: QName                       # PartnersDimension
    # Six elements required in every partner context (NVAD-E-1210)
    mandatoryPartnerQns: frozenset[QName]
    bir52PartnerFullNameQn: QName
    bir52PartnerPrecedentPartnerQn: QName
    bir52PartnerPersonalAssessmentQn: QName
    bir52PartnerProfitLossSharingRatioQn: QName
    bir52PartnerAllocationOfAssessableProfitsQn: QName  # BIR52ProprietorPartnerAllocationOfAssessableProfitsAdjustedLoss
    bir52PartnerHkidOrBrnQn: QName                  # BIR52ProprietorPartnerHKIDOrBRNumber
    bir52PartnerDateEnteredQn: QName
    bir52PartnerDateLeftQn: QName

    # Combined FS (nvad_combined_fs)
    accountsPreparedAtConsolidatedLevelQn: QName  # ird_tc:AccountsPreparedAtConsolidatedLevel (NVAD-E-1291/1292)
    tcProfitLossBeforeTaxQn: QName     # ird_tc:ProfitLossBeforeTax
    fsEquityQn: QName                  # ird_fs:Equity  (NVAD-E-1290)
    fsPeEquityQn: QName                # ird_fs_pe:Equity (NVAD-E-1290, PE taxonomy)
    fsRevenueQn: QName                 # ird_fs:Revenue (NVAD-E-1291)
    fsPeRevenueQn: QName               # ird_fs_pe:Revenue (NVAD-E-1291, PE taxonomy)
    fsProfitLossBeforeTaxQn: QName     # ird_fs:ProfitLossBeforeTax (NVAD-E-1292, 1390)
    fsPeProfitLossBeforeTaxQn: QName   # ird_fs_pe:ProfitLossBeforeTax (NVAD-E-1292, PE taxonomy)
    fsAssetsQn: QName                  # ird_fs:Assets  (NVAD-E-1300)
    fsPeAssetsQn: QName                # ird_fs_pe:Assets (NVAD-E-1300, PE taxonomy)
    fsEquityAndLiabilitiesQn: QName    # ird_fs:EquityAndLiabilities (NVAD-E-1300)
    fsPeEquityAndLiabilitiesQn: QName  # ird_fs_pe:EquityAndLiabilities (NVAD-E-1300, PE taxonomy)

    # HKSIC code (nvad_structural, NVAD-E-0170/0180/0190)
    hksicCodeQn: QName
    hksicCodeRegex: re.Pattern[str]     # r'^\d{6}$'
    validHksicCodes: frozenset[str]

    # Compiled regexes
    irdFileNumberRegex: re.Pattern[str]     # r'^\d{2}/\d{8}$'
    yearOfAssessmentRegex: re.Pattern[str]  # r'^20(\d{2})/(\d{2})$'
    hkidRegex: re.Pattern[str]              # HKID: 1-2 letters + 6 digits + check digit
    brnRegex: re.Pattern[str]               # BRN: exactly 8 digits

    # Identity hash for caching.
    def __hash__(self) -> int:
        return id(self)

    def _exclusiveQnCount(self, modelXbrl: ModelXbrl, qnames: frozenset[QName]) -> int:
        return sum(
            1 for qn in qnames
            if hasValidNonNilFactByQname(modelXbrl, qn)
        )

    @lru_cache(1)
    def isBir52(self, modelXbrl: ModelXbrl) -> bool:
        """True when the document is a BIR52 (partnership/proprietorship) filing.

        Detection is based on a higher count of BIR52-exclusive concepts
        than BIR51-exclusive concepts.
        """
        n52 = self._exclusiveQnCount(modelXbrl, self.bir52ExclusiveQns)
        n51 = self._exclusiveQnCount(modelXbrl, self.bir51ExclusiveQns)
        if n51 == 0 and n52 == 0:
            return False  # FS-only / no exclusive facts → keep today's BIR51 default
        return n52 > n51

    def isBir51(self, modelXbrl: ModelXbrl) -> bool:
        """True when the document is a BIR51 (corporation) filing.

        BIR51 is assumed unless BIR52-exclusive concepts outnumber BIR51-exclusive ones.
        """
        return not self.isBir52(modelXbrl)

    @lru_cache(1)
    def getSchemaRefsByDocument(
        self,
        modelXbrl: ModelXbrl,
    ) -> dict[str, list[ModelObject]]:
        """Return each Inline XBRL document's ``link:schemaRef`` elements,
        keyed by document URI.

        Grouped per physical document so callers can detect *within a
        single file* whether more than one schemaRef is present. A combined
        TC+FS filing normally has two documents, each with exactly one
        schemaRef, and must not be mistaken for a single document with two.

        The returned elements are suitable as ``modelObject`` on a
        :class:`~arelle.utils.validate.Validation.Validation`.
        """
        refsByDoc: dict[str, list[ModelObject]] = {}
        for doc in modelXbrl.urlDocs.values():
            if doc.type == ModelDocumentType.INLINEXBRL:
                root = doc.xmlRootElement
                if root is None:
                    continue
                refsByDoc[doc.uri] = list(root.iter(SCHEMA_REF_TAG))
        return refsByDoc

    @lru_cache(1)
    def getSchemaRefHrefs(self, modelXbrl: ModelXbrl) -> list[str]:
        """Return all non-empty ``xlink:href`` values from ``link:schemaRef``
        elements across the IXDS.

        Flattens hrefs from :meth:`getSchemaRefsByDocument` — appropriate
        for "does any file reference a valid entry point" checks.
        """
        return [
            href
            for refs in self.getSchemaRefsByDocument(modelXbrl).values()
            for ref in refs
            if (href := (ref.get(XLINK_HREF, "") or ""))
        ]

    @lru_cache(1)
    def factsByPartnerContext(
        self,
        modelXbrl: ModelXbrl,
    ) -> dict[str, set[ModelFact]]:
        """Group non-nil facts by their BIR52 partner typed-dimension member.

        Returns a ``dict`` whose keys are the string value of each partner
        typed-dimension member (e.g. ``"1"``, ``"2"``…) and whose values are
        the set of non-nil facts filed in that partner's context.

        Facts that do not carry the partner dimension are excluded.
        """
        partnerDimQn = self.partnersDimensionQn
        groups: dict[str, set[ModelFact]] = {}

        for fact in modelXbrl.facts:
            if not isValidNonNilFact(fact):
                continue
            ctx = fact.context
            if ctx is None:
                continue
            dimValue = ctx.qnameDims.get(partnerDimQn)
            if dimValue is None:
                continue
            # For a typed dimension the member is an lxml element whose
            # text content is the partner identifier.
            typedMember = getattr(dimValue, "typedMember", None)
            if typedMember is None:
                continue
            memberKey: str = (typedMember.text or "").strip()
            if not memberKey:
                continue
            groups.setdefault(memberKey, set()).add(fact)

        return groups

    @lru_cache(1)
    def _monetaryFactsByNamespace(
        self,
        modelXbrl: ModelXbrl,
    ) -> dict[str, set[ModelFact]]:
        """Scan once and group monetary facts by concept namespace."""
        grouped: dict[str, set[ModelFact]] = {}
        for fact in modelXbrl.facts:
            if not isValidNonNilFact(fact):
                continue
            concept = fact.concept
            if concept is None:
                continue
            namespace = fact.qname.namespaceURI
            if namespace is None or not concept.isMonetary:
                continue
            grouped.setdefault(namespace, set()).add(fact)
        return grouped

    def getMonetaryFacts(
        self,
        modelXbrl: ModelXbrl,
        namespace: str,
    ) -> set[ModelFact]:
        """Return all non-nil facts in *namespace* that are monetary"""
        return self._monetaryFactsByNamespace(modelXbrl).get(namespace, set())
