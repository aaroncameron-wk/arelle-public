"""
See COPYRIGHT.md for copyright information.
"""
from __future__ import annotations

from typing import Iterable

import fnmatch
from pathlib import Path

from arelle import XmlUtil
from arelle.ModelDocument import ModelDocument
from arelle.ModelObject import ModelObject
from arelle.ModelTestcaseObject import ModelTestcaseVariation
from arelle.ModelValue import QName
from arelle.RuntimeOptions import RuntimeOptions
from arelle.api.Session import Session
from test_engine.ErrorLevel import ErrorLevel
from test_engine.TestEngineOptions import TestEngineOptions
from test_engine.TestcaseConstraint import TestcaseConstraint
from test_engine.TestcaseConstraintSet import TestcaseConstraintSet
from test_engine.TestcaseVariation import TestcaseVariation

CALC_MODES_MAP = {
    'truncate': 'truncation',
}
CWD = Path.cwd()
PARAMETER_SEPARATOR = '\n'
TARGET_SUFFIX_SEPARATOR = '|'


def _getCalcMode(testcaseVariation: ModelTestcaseVariation) -> str:
    """
    Determine a single calculation mode for the variation.
    Raises an AssertionError if it is ambiguous.
    :param testcaseVariation:
    :return: The calculation mode to use for this testcase variation.
    """
    calcModes = set()
    for resultElt in XmlUtil.descendants(testcaseVariation, None, "result"):
        if not isinstance(resultElt, ModelObject):
            continue
        calcModes.add(resultElt.attr('{https://xbrl.org/2023/conformance}mode'))
    assert len(calcModes) == 1, f"Multiple calculation modes found: {calcModes}."
    calcMode = next(iter(calcModes))
    calcMode = CALC_MODES_MAP.get(calcMode, calcMode)
    return calcMode


def _getConstraints(testcaseVariation: ModelTestcaseVariation) -> list[TestcaseConstraint]:
    constraints = []
    expected = testcaseVariation.expected or 'valid'
    if not isinstance(expected, list):
        expected = [expected]
    for e in expected:
        # TODO: table element
        # TODO: testcase element
        # TODO: testGroup element
        # TODO: result element
        # TODO: assert elements
        # TODO: assertionTests elements
        if e == 'valid':
            pass
        elif e == 'invalid':
            constraints.append(TestcaseConstraint(
                pattern='*',  # matches any code
            ))
        elif isinstance(e, QName):
            constraints.append(TestcaseConstraint(
                qname=e,
            ))
        elif isinstance(e, str):
            constraints.append(TestcaseConstraint(
                pattern=e,
            ))
        elif isinstance(e, dict):
            for pattern, assertions in e.items():
                satisfiedCount, notSatisfiedCount = assertions
                countMap = {
                    ErrorLevel.SATISIFED: satisfiedCount,
                    ErrorLevel.NOT_SATISFIED: notSatisfiedCount,
                }
                for level, count in countMap.items():
                    for i in range(0, count):
                        constraints.append(TestcaseConstraint(
                            pattern=pattern,
                            level=level,
                        ))
        else:
            raise ValueError(f"Unexpected expected error type: {type(e)}")

    if testcaseVariation.resultTableUri is not None:
        # Result table URIs are not currently validated
        pass

    expectedWarnings = testcaseVariation.expectedWarnings or []
    for warning in expectedWarnings:
        if isinstance(warning, QName):
            constraints.append(TestcaseConstraint(
                qname=warning,
                level=ErrorLevel.ERROR,  # TODO: Differentiate between errors and warnings
            ))
        elif isinstance(warning, str):
            constraints.append(TestcaseConstraint(
                pattern=warning,
                level=ErrorLevel.ERROR,  # TODO: Differentiate between errors and warnings
            ))
        else:
            raise ValueError(f"Unexpected expected warning type: {type(e)}")
    return constraints


def _getParameters(testcaseVariation: ModelTestcaseVariation) -> list[str]:
    parameters = [
        f'{k.clarkNotation}={v[1]}'
        for k, v in testcaseVariation.parameters.items()
    ]
    assert all(PARAMETER_SEPARATOR not in parameter for parameter in parameters), \
        'Parameter separator found in parameter key or value.'
    return parameters


def _iterTargets(testcaseVariation: ModelTestcaseVariation) -> Iterable[str]:
    targets = [
        instElt.get("target")
        for resultElt in testcaseVariation.iterdescendants("{*}result")
        for instElt in resultElt.iterdescendants("{*}instance")
    ] or [None]
    for target in targets:
        if len(targets) > 1 and target is None:
            target = "(default)"
        yield target


def _loadTestcaseDoc(doc: ModelDocument, testEngineOptions: TestEngineOptions, testcaseVariations: list[TestcaseVariation]) -> None:
    docPath = Path(doc.uri)
    docPath = docPath.relative_to(CWD) if docPath.is_relative_to(CWD) else docPath
    for testcaseVariation in doc.testcaseVariations:
        base = testcaseVariation.base
        assert base is not None
        if base.startswith("file:\\"):
            base = base[6:]
        for target in _iterTargets(testcaseVariation):
            testcaseVariation.ixdsTarget = target
            assert TARGET_SUFFIX_SEPARATOR not in testcaseVariation.id, \
                f"The '{TARGET_SUFFIX_SEPARATOR}' character is used internally as a separator " + \
                "and can not be included in a testcase variation ID."
            localId = f"{testcaseVariation.id}" + (f"{TARGET_SUFFIX_SEPARATOR}{target}" if target else "")
            fullId = f"{base}:{localId}"

            if testEngineOptions.filters:
                if not any(fnmatch.fnmatch(fullId, _filter) for _filter in testEngineOptions.filters):
                    continue # TODO: Only filter here

            calcMode = _getCalcMode(testcaseVariation)
            constraints = _getConstraints(testcaseVariation)
            parameters = _getParameters(testcaseVariation)

            compareInstanceUri = None
            compareFormulaOutputUri = None
            instanceUri = testcaseVariation.resultXbrlInstanceUri
            if instanceUri:
                compareInstanceUri = Path(doc.modelXbrl.modelManager.cntlr.webCache.normalizeUrl(instanceUri, testcaseVariation.base))
                if testEngineOptions.compareFormulaOutput:
                    compareFormulaOutputUri = compareInstanceUri
                    compareInstanceUri = None

            testcaseConstraintSet = TestcaseConstraintSet(
                constraints=constraints,
                matchAll=testEngineOptions.matchAll,
            )
            testcaseVariations.append(TestcaseVariation(
                id=localId,
                fullId=fullId,
                name=testcaseVariation.name,
                description=testcaseVariation.description,
                base=base,
                readFirstUris=testcaseVariation.readMeFirstUris,
                shortName=f"{docPath}:{localId}",
                status=testcaseVariation.status,
                testcaseConstraintSet=testcaseConstraintSet,
                blockedCodePattern=testcaseVariation.blockedMessageCodes,
                calcMode=calcMode,
                parameters=PARAMETER_SEPARATOR.join(parameters),
                ignoreLevels=testEngineOptions.ignoreLevels,
                compareInstanceUri=compareInstanceUri,
                compareFormulaOutputUri=compareFormulaOutputUri,
                inlineTarget=target,
            ))


def loadTestcaseIndex(index_path: str, testEngineOptions: TestEngineOptions) -> list[TestcaseVariation]:
    """
    Use the Arelle Session API to load an XML testcase index and build variations for running in the test engine.
    TODO: Don't rely on ModelTestcaseVariation.
    :param index_path:
    :param testEngineOptions:
    :return:
    """
    runtimeOptions = RuntimeOptions(
        entrypointFile=index_path,
        keepOpen=True,
    )
    with Session() as session:
        session.run(
            runtimeOptions,
        )
        models = session.get_models()
        docs = []
        testcaseVariations = []
        for model in models:
            for doc in model.urlDocs.values():
                if hasattr(doc, 'testcaseVariations') and doc.testcaseVariations is not None:
                    docs.append(doc)
        for doc in docs:
            _loadTestcaseDoc(doc, testEngineOptions, testcaseVariations)
        return testcaseVariations
