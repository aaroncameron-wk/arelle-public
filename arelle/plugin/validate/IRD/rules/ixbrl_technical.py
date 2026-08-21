"""
See COPYRIGHT.md for copyright information.

iXBRL Technical rules — ``<link:schemaRef>`` entry point validation.

Rules implemented here:
  553-E-0467/0497/0534/0543  schemaRef href is invalid, malformed, or does
                              not resolve to any recognised taxonomy shape
  553-E-0468                 schemaRef href is a recognised IRD taxonomy
                              entry point but not the latest version
  553-E-0470/0486/0500       schemaRef href's version date does not match
                              any released IRD taxonomy version
  553-E-0498                 schemaRef href is a well-formed reference to
                              a different (non-IRD) taxonomy
  553-E-0535/0536/0544/0552  document contains more than one schemaRef
                              element

Each family of related codes shares a single root cause per the IRD's
own documentation, so a single rule function yields all codes in the
family together as a ``codes`` tuple; Arelle logs the first code in
the tuple whose prefix matches the active disclosure system's validation
type (here, every code in every tuple starts with "IRD.", so the
first-listed code is always the one actually logged) and the conformance
harness treats a match against *any* of the testcase's listed ``<error>``
codes as a pass.
"""
from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any
from urllib.parse import urlparse

from arelle.ValidateXbrl import ValidateXbrl
from arelle.typing import TypeGetText
from arelle.utils.PluginHooks import ValidationHook
from arelle.utils.validate.Decorator import validation
from arelle.utils.validate.Validation import Validation
from . import schemaRefHref
from ..DisclosureSystems import ALL_IRD_DISCLOSURE_SYSTEMS
from ..PluginValidationDataExtension import PluginValidationDataExtension

_: TypeGetText

# A well-formed IRD taxonomy href: a version-dated path segment followed
# by an entry point filename that repeats the same date.
IRD_HREF_RE = re.compile(
    r"^https?://xbrl\.ird\.gov\.hk/taxonomy/"
    r"(?P<date>\d{4}-\d{2}-\d{2})/(?P<filename>[^/]+\.xsd)$"
)

# The filename shape used by every IRD TC/FS entry point, regardless of
# version date (checked separately against IRD_HREF_RE's path date).
ENTRY_POINT_FILENAME_RE = re.compile(
    r"^ird_(?:tc|tc-zh-hk|fs|fs_pe)_entry_point_\d{4}-\d{2}-\d{2}\.xsd$"
)

# Hosts of other well-known XBRL taxonomies. A schemaRef href resolving
# to one of these (rather than to an unrecognised/non-existent domain)
# is a well-formed reference to a real, identifiable, but wrong
# taxonomy — distinct from a malformed or dead-end URL.
OTHER_TAXONOMY_HOSTS = (
    "xbrl.ifrs.org",
    "xbrl.fasb.org",
    "xbrl.sec.gov",
    "xbrl.us",
    "xbrl.org",
    "eiopa.europa.eu",
    "esma.europa.eu",
)


def _isOtherKnownTaxonomy(href: str) -> bool:
    """True if *href* resolves to a host of a real, non-IRD taxonomy."""
    try:
        host = urlparse(href).netloc.lower()
    except ValueError:
        return False
    return any(
        host == known or host.endswith(f".{known}")
        for known in OTHER_TAXONOMY_HOSTS
    )


def _classifyHref(
    href: str, pluginData: PluginValidationDataExtension
) -> str:
    """Classify a single schemaRef ``href`` for the 553-E rule family.

    Returns one of:
      "valid"                — a recognised, latest-version entry point
      "old_version"           — recognised IRD entry point shape, but an
                                older (non-latest) released version (0468)
      "unrecognised_version"  — recognised IRD entry point shape, but a
                                version date that was never released
                                (0470/0486/0500)
      "wrong_taxonomy"        — a well-formed href to a different, real
                                taxonomy, not IRD's (0498)
      "invalid"               — malformed, empty, unrecognised, or a
                                dead-end URL (0467/0497/0534/0543)
    """
    if href in pluginData.allValidEntryPoints:
        return "valid"

    match = IRD_HREF_RE.match(href)
    if match is None:
        if _isOtherKnownTaxonomy(href):
            return "wrong_taxonomy"
        return "invalid"

    date = match.group("date")
    filename = match.group("filename")
    if not ENTRY_POINT_FILENAME_RE.match(filename):
        return "invalid"

    if date == pluginData.latestVersionDate:
        # Right domain, right shape, latest date — yet not a recognised
        # entry point (e.g. a taxonomy/language variant that does not
        # exist). Treat as unrecognised rather than a version mismatch.
        return "invalid"
    if date in pluginData.releasedVersionDates:
        return "old_version"
    return "unrecognised_version"


def _iterSchemaRefs(
    pluginData: PluginValidationDataExtension,
    modelXbrl: Any,
) -> Iterable[tuple[Any, str]]:
    """Yield ``(ref, href)`` for every ``link:schemaRef`` in the IXDS."""
    for refs in pluginData.getSchemaRefsByDocument(modelXbrl).values():
        for ref in refs:
            yield ref, schemaRefHref(ref)


@validation(
    hook=ValidationHook.XBRL_FINALLY,
    disclosureSystems=ALL_IRD_DISCLOSURE_SYSTEMS,
)
def rule_553_e_invalid_entry_point(
    pluginData: PluginValidationDataExtension,
    val: ValidateXbrl,
    *args: Any,
    **kwargs: Any,
) -> Iterable[Validation]:
    """553-E-0467/0497/0534/0543: schemaRef entry point is invalid or
    unrecognised.

    Fires for any ``<link:schemaRef>`` href that is malformed, empty, or
    otherwise does not resolve to any recognised taxonomy shape —
    including a dead-end/non-existent URL such as
    ``http://example.com/nonexistent.xsd``. Distinct from
    553-E-0498 (a well-formed reference to a *different*, real
    taxonomy) and from 553-E-0470/0486/0500 (a recognised IRD entry
    point shape with an unreleased version date).
    """
    for ref, href in _iterSchemaRefs(pluginData, val.modelXbrl):
        if _classifyHref(href, pluginData) == "invalid":
            yield Validation.error(
                codes=(
                    "IRD.553-E-0467",
                    "IRD.553-E-0497",
                    "IRD.553-E-0534",
                    "IRD.553-E-0543",
                ),
                msg=_(
                    "schemaRef href '%(href)s' does not reference a "
                    "valid or recognised IRD taxonomy entry point."
                ),
                modelObject=ref,
                href=href,
            )


@validation(
    hook=ValidationHook.XBRL_FINALLY,
    disclosureSystems=ALL_IRD_DISCLOSURE_SYSTEMS,
)
def rule_553_e_0468(
    pluginData: PluginValidationDataExtension,
    val: ValidateXbrl,
    *args: Any,
    **kwargs: Any,
) -> Iterable[Validation]:
    """553-E-0468: schemaRef does not reference the latest IRD TC
    taxonomy version.

    Fires when the href is shaped like a recognised IRD taxonomy entry
    point and its version date is a previously released version, but
    not the current latest (``pluginData.latestVersionDate``).
    """
    for ref, href in _iterSchemaRefs(pluginData, val.modelXbrl):
        if _classifyHref(href, pluginData) == "old_version":
            yield Validation.error(
                codes="IRD.553-E-0468",
                msg=_(
                    "schemaRef href '%(href)s' references a superseded "
                    "IRD taxonomy version; the latest version is "
                    "%(latestVersion)s."
                ),
                modelObject=ref,
                href=href,
                latestVersion=pluginData.latestVersionDate,
            )


@validation(
    hook=ValidationHook.XBRL_FINALLY,
    disclosureSystems=ALL_IRD_DISCLOSURE_SYSTEMS,
)
def rule_553_e_unrecognised_version(
    pluginData: PluginValidationDataExtension,
    val: ValidateXbrl,
    *args: Any,
    **kwargs: Any,
) -> Iterable[Validation]:
    """553-E-0470/0486/0500: schemaRef references an invalid/unreleased
    taxonomy version.

    Fires when the href is shaped like a recognised IRD taxonomy entry
    point but its version date does not match any version the IRD has
    ever released (``pluginData.releasedVersionDates``) — distinct
    from 553-E-0468, where the version date *was* released but is not
    the latest.
    """
    for ref, href in _iterSchemaRefs(pluginData, val.modelXbrl):
        if _classifyHref(href, pluginData) == "unrecognised_version":
            yield Validation.error(
                codes=("IRD.553-E-0470", "IRD.553-E-0486", "IRD.553-E-0500"),
                msg=_(
                    "schemaRef href '%(href)s' references a taxonomy "
                    "version date that does not match any released "
                    "IRD taxonomy version."
                ),
                modelObject=ref,
                href=href,
            )


@validation(
    hook=ValidationHook.XBRL_FINALLY,
    disclosureSystems=ALL_IRD_DISCLOSURE_SYSTEMS,
)
def rule_553_e_0498(
    pluginData: PluginValidationDataExtension,
    val: ValidateXbrl,
    *args: Any,
    **kwargs: Any,
) -> Iterable[Validation]:
    """553-E-0498: schemaRef does not reference the IRD TC taxonomy
    (wrong taxonomy).

    Fires when the href is a well-formed reference to a real,
    identifiable taxonomy other than the IRD's (e.g. IFRS or US-GAAP),
    as opposed to a malformed or non-existent URL (covered by
    553-E-0467/0497/0534/0543).
    """
    for ref, href in _iterSchemaRefs(pluginData, val.modelXbrl):
        if _classifyHref(href, pluginData) == "wrong_taxonomy":
            yield Validation.error(
                codes="IRD.553-E-0498",
                msg=_(
                    "schemaRef href '%(href)s' references a taxonomy "
                    "other than the IRD TC/FS taxonomy."
                ),
                modelObject=ref,
                href=href,
            )


@validation(
    hook=ValidationHook.XBRL_FINALLY,
    disclosureSystems=ALL_IRD_DISCLOSURE_SYSTEMS,
)
def rule_553_e_multiple_schema_refs(
    pluginData: PluginValidationDataExtension,
    val: ValidateXbrl,
    *args: Any,
    **kwargs: Any,
) -> Iterable[Validation]:
    """553-E-0535/0536/0544/0552: document contains more than one
    schemaRef element.

    The IRD requires exactly one taxonomy entry point *per data file*;
    two or more ``<link:schemaRef>`` elements within the same physical
    document — whether duplicates or references to different entry
    points — triggers this error family. Checked per-document (not
    across the whole IXDS) so a normal combined TC+FS filing, which
    legitimately has two documents each with their own single
    schemaRef, is not mistaken for this violation.
    """
    for uri, refs in pluginData.getSchemaRefsByDocument(val.modelXbrl).items():
        if len(refs) > 1:
            yield Validation.error(
                codes=(
                    "IRD.553-E-0535",
                    "IRD.553-E-0536",
                    "IRD.553-E-0544",
                    "IRD.553-E-0552",
                ),
                msg=_(
                    "Document '%(uri)s' contains %(count)s "
                    "link:schemaRef elements; exactly one taxonomy "
                    "entry point is permitted per data file."
                ),
                modelObject=refs,
                uri=uri,
                count=len(refs),
            )
