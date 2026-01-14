"""
See COPYRIGHT.md for copyright information.
"""
from __future__ import annotations
import argparse
import fnmatch
import json
import multiprocessing
import os
from collections import defaultdict
from pathlib import Path

import re
import time
from urllib.parse import unquote

from arelle import XbrlConst
from arelle.ModelObject import ModelObject
from arelle.ModelValue import QName
from arelle.RuntimeOptions import RuntimeOptions
from arelle.UrlUtil import IXDS_DOC_SEPARATOR, IXDS_SURROGATE
from arelle.api.Session import Session
from test_engine import XmlTestcaseLoader
from test_engine.ActualError import ActualError
from test_engine.ErrorLevel import ErrorLevel
from test_engine.TestEngineOptions import TestEngineOptions
from test_engine.TestcaseCompareContext import TestcaseCompareContext
from test_engine.TestcaseConstraint import TestcaseConstraint
from test_engine.TestcaseConstraintResult import TestcaseConstraintResult
from test_engine.TestcaseConstraintSet import TestcaseConstraintSet
from test_engine.TestcaseResult import TestcaseResult
from test_engine.TestcaseVariation import TestcaseVariation

CWD = Path.cwd()
PARAMETER_SEPARATOR = '\n'
TARGET_SUFFIX_SEPARATOR = '|'
DEFAULT_PLUGIN_OPTIONS = {
    'EDGAR/render': {
        'keepFilingOpen': True,
    },
    'xule': {
        "xule_time": 2.0,
        "xule_rule_stats_log": True,
    }
}
PROHIBITED_PLUGIN_OPTIONS = frozenset({
    'inlineTarget',
})
PROHIBITED_RUNTIME_OPTIONS = frozenset({
    'compareFormulaOutput',
    'compareInstance',
    'entrypointFile',
    'keepOpen',
    'logFile',
    'parameterSeparator',
    'parameters',
    'validate',
})


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i', '--index',
        help="Path or URL to the testcase index file.",
        required=True,
        type=str
    )
    parser.add_argument(
        '--custom-compare-patterns',
        help="Custom comparison of expected/actual error codes. Format: \"{expected}|{actual}\". \"~\" in actual is replaced with the expected code.",
        required=False,
        action='append',
    )
    parser.add_argument(
        '-f', '--filters',
        help="Filter patterns to determine testcase variations to include.",
        required=False,
        action='append',
    )
    parser.add_argument(
        '-l', '--log-directory',
        help="Directory to write log files and test reports to.",
        required=False,
        type=str
    )
    parser.add_argument(
        '-m', '--match-all',
        help="Whether tests results need to match all of the expected errors/warnings to pass.",
        required=False,
        action='store_true',
    )
    parser.add_argument(
        '-p', '--parallel',
        help="Run testcases in parallel.",
        required=False,
        action='store_true',
    )
    parser.add_argument(
        '-o', '--options',
        help="JSON (or path to .json file) defining Arelle runtime options.",
        required=True,
        type=str
    )
    return parser.parse_args()


def normPath(path: Path) -> str:
    path = path.relative_to(CWD) if path.is_relative_to(CWD) else path
    pathStr = str(path)
    if pathStr.startswith("file:\\"):
        pathStr = pathStr[6:]
    return unquote(pathStr)


def buildEntrypointUris(uris: list[Path]) -> list[str]:
    uris = [
        uri.relative_to(Path.cwd()) if uri.is_relative_to(Path.cwd()) else uri
        for uri in uris
    ]
    if len(uris) > 1:
        if all(uri.suffix in ('.htm', '.html', '.xhtml') for uri in uris):
            docsetSurrogatePath = normPath(uris[0].parent) + os.sep + IXDS_SURROGATE
            return [docsetSurrogatePath + IXDS_DOC_SEPARATOR.join(normPath(uri) for uri in uris)]
    return [normPath(uri) for uri in uris]


def loadTestcaseIndex(index_path: str, testEngineOptions: TestEngineOptions) -> list[TestcaseVariation]:
    if index_path.endswith('.xml'):
        return XmlTestcaseLoader.loadTestcaseIndex(index_path, testEngineOptions)
    raise ValueError(f'No testcase loader available for \"{index_path}\".')


class TestEngine:
    _options: TestEngineOptions

    def __init__(self, options: TestEngineOptions):
        self._options = options

    def runTestcaseVariationArgs(self, inputArgs: tuple[TestcaseVariation]) -> TestcaseResult:
        testcaseVariation, = inputArgs
        return self.runTestcaseVariation(testcaseVariation)

    def filterTestcaseVariation(self, testcaseVariation: TestcaseVariation, filters: list[str]) -> bool:
        if not filters:
            return True
        variationId = testcaseVariation.fullId
        for filter in filters:
            if fnmatch.fnmatch(variationId, filter):
                return True
        return False

    def logFilename(self, name: str) -> str:
        name = re.sub(r'[<>:"|?*\x00-\x1F]', '_', name)
        return name.strip().strip('.')

    def runTestcaseVariation(
            self,
            testcaseVariation: TestcaseVariation,
    ) -> TestcaseResult:
        if not self.filterTestcaseVariation(testcaseVariation, self._options.filters):
            return TestcaseResult(
                testcaseVariation=testcaseVariation,
                appliedConstraintSet=TestcaseConstraintSet(constraints=[], matchAll=self._options.matchAll),
                actualErrors=[],
                constraintResults=[],
                passed=True,
                skip=True,
                duration_seconds=0,
                blockedErrors={},
            )
        entrypointUris = buildEntrypointUris([
            Path(testcaseVariation.base).parent.joinpath(Path(readMeFirstUri))
            for readMeFirstUri in testcaseVariation.readFirstUris
        ])

        dynamicOptions = dict(self._options.options)
        for prohibitedOption in PROHIBITED_RUNTIME_OPTIONS:
            assert prohibitedOption not in dynamicOptions, f'The option "{prohibitedOption}" is reserved by the test engine.'
        if not dynamicOptions.get('pluginOptions'):
            dynamicOptions['pluginOptions'] = {}
        pluginOptions = dynamicOptions['pluginOptions']
        for prohibitedOption in PROHIBITED_PLUGIN_OPTIONS:
            assert prohibitedOption not in pluginOptions, f'The plugin option "{prohibitedOption}" is reserved by the test engine.'

        if testcaseVariation.calcMode is not None:
            assert dynamicOptions.get('calcs', testcaseVariation.calcMode) == testcaseVariation.calcMode, \
                'Conflicting "calcs" values from testcase variation and user input.'
            dynamicOptions['calcs'] = testcaseVariation.calcMode
        if 'plugins' in dynamicOptions:
            for plugin in dynamicOptions['plugins'].split('|'):
                pluginOptions |= dynamicOptions.get('pluginOptions', {}) | DEFAULT_PLUGIN_OPTIONS.get(plugin, {})

        if testcaseVariation.inlineTarget:
            pluginOptions['inlineTarget'] = testcaseVariation.inlineTarget

        entrypointFile = '|'.join(entrypointUris)
        runtimeOptions = RuntimeOptions(
            entrypointFile=entrypointFile,
            keepOpen=True,
            validate=True,
            logFile=normPath(self._options.logDirectory / f"{self.logFilename(testcaseVariation.shortName)}-log.txt") if self._options.logDirectory else None,
            parameters=testcaseVariation.parameters,
            parameterSeparator=PARAMETER_SEPARATOR,
            compareFormulaOutput=normPath(testcaseVariation.compareFormulaOutputUri) if testcaseVariation.compareFormulaOutputUri else None,
            compareInstance=normPath(testcaseVariation.compareInstanceUri) if testcaseVariation.compareInstanceUri else None,
            **dynamicOptions
        )
        runtimeOptionsJson = json.dumps({k: v for k, v in vars(runtimeOptions).items() if v is not None}, indent=4, sort_keys=True)
        if runtimeOptions.logFile is not None:
            Path(runtimeOptions.logFile).parent.mkdir(parents=True, exist_ok=True)
            with open(runtimeOptions.logFile, 'w') as f:
                f.write(f'Running [{testcaseVariation.fullId}] with options:\n{runtimeOptionsJson}\n------\n')
        with Session() as session:
            start_ts = time.perf_counter_ns()
            session.run(
                runtimeOptions,
                # logHandler=StructuredMessageLogHandler() if 'logFile' not in self._options.options else None, TODO
            )
            duration_seconds = (time.perf_counter_ns() - start_ts) / 1_000_000_000
            # logs = session.get_log_messages()
            actualErrors = []
            errors: list[str | None] = []
            assert session._cntlr is not None
            errors.extend(session._cntlr.errors)
            for model in session.get_models():
                errors.extend(model.errors)
            for error in errors:
                if isinstance(error, dict):
                    for code, counts in error.items():
                        assert isinstance(code, str)
                        satisfiedCount, notSatisfiedCount, okCount, warningCount, errorCount = counts
                        countMap = {
                            ErrorLevel.SATISIFED: satisfiedCount,
                            ErrorLevel.NOT_SATISFIED: notSatisfiedCount,
                            ErrorLevel.OK: okCount,
                            ErrorLevel.WARNING: warningCount,
                            # Also captured as a separate "error"
                            # ErrorLevel.ERROR: errorCountÎ
                        }
                        for level, count in countMap.items():
                            if level in testcaseVariation.ignoreLevels:
                                continue
                            for i in range(0, count):
                                actualErrors.append(ActualError(
                                    code=code,
                                    level=level
                                ))
                    continue
                assert isinstance(error, str), f"Received actual error of unexpected type \"{type(error)}\"."
                # if error is None:
                #     print("Warning: Detected \"None\" actual error. Defaulted to \"ERROR\"")  # TODO
                #     error = "ERROR"
                # if isinstance(error, QName) or error is None:
                #     print(f"Warning: Flattened actual error QName to string: {error.clarkNotation}")  # TODO
                #     error = str(error)
                actualErrors.append(ActualError(
                    code=error,
                    level=ErrorLevel.ERROR,
                ))
            result = self.buildResult(
                testcaseVariation=testcaseVariation,
                actualErrors=actualErrors,
                duration_seconds=duration_seconds,
                additionalConstraints=self._options.additionalConstraints
            )
            return result


    def runTestcaseVariationsInParallel(
            self,
            testcaseVariations: list[TestcaseVariation],
    ) -> list[TestcaseResult]:
        tasks = [
            (testcaseVariation,)
            for testcaseVariation in testcaseVariations
        ]
        # Some parts of Arelle and it's plugins have global state that is not reset.
        # Setting maxtasksperchild helps ensure global state does not persist between
        # two tasks run by the same child process.
        with multiprocessing.Pool(maxtasksperchild=1) as pool:
            results = pool.map(self.runTestcaseVariationArgs, tasks)
            for result in results:
                if not result.skip:
                    print(result.report())
            return results

    def runTestcaseVariationsInSeries(
            self,
            testcaseVariations: list[TestcaseVariation],
    ) -> list[TestcaseResult]:
        results = []
        for testcaseVariation in testcaseVariations:
            result = self.runTestcaseVariation(testcaseVariation)
            if not result.skip:
                print(result.report())
            results.append(result)
        return results


    def _normalizedConstraints(
            self,
            constraints: list[TestcaseConstraint]
    ) -> list[TestcaseConstraint]:
        normalizedConstraintsMap: dict[tuple[QName | None, str | None, ErrorLevel], int] = {}
        for constraint in constraints:
            key = (
                constraint.qname,
                constraint.pattern,
                constraint.level,
            )
            if key not in normalizedConstraintsMap:
                normalizedConstraintsMap[key] = 0
            normalizedConstraintsMap[key] += constraint.count
        normalizedConstraints = [
            TestcaseConstraint(
                qname=_qname,
                pattern=_pattern,
                count=_count,
                level=_level,
            )
            for (
                _qname,
                _pattern,
                _level,
            ), _count in normalizedConstraintsMap.items()
        ]
        return normalizedConstraints


    def blockCodes(self, actualErrors: list[ActualError], pattern: str) -> tuple[list[ActualError], dict[str, int]]:
        results = []
        blockedCodes: dict[str, int] = defaultdict(int)
        if not pattern:
            return actualErrors, blockedCodes
        compiledPattern = re.compile(re.sub(r'\\(.)', r'\1', pattern))
        for actualError in actualErrors:
            if compiledPattern.match(actualError.code):
                blockedCodes[actualError.code] += 1
                continue
            results.append(actualError)
        return results, blockedCodes


    def getDiff(self, testcaseConstraintSet: TestcaseConstraintSet, actualErrorCounts: dict[tuple[str, ErrorLevel], int] ) -> dict[tuple[str | QName, ErrorLevel], int]:
        diff = {}
        compareContext = TestcaseCompareContext(
            customComparePatterns=self._options.customComparePatterns,
            localNameMap=XbrlConst.errMsgNamespaceLocalNameMap,
            prefixNamespaceUriMap=XbrlConst.errMsgPrefixNS,
        )
        for constraint in testcaseConstraintSet.constraints:
            keyVal = constraint.qname or constraint.pattern
            assert keyVal is not None
            constraintKey = (keyVal, constraint.level)
            matchCount = 0
            for actualKey, count in actualErrorCounts.items():
                actualError, level = actualKey
                if level != constraint.level:
                    continue
                if compareContext.compare(constraint, actualError):
                    if count > constraint.count:
                        count = constraint.count
                    matchCount += count
                    actualErrorCounts[actualKey] -= count
            diff[constraintKey] = matchCount - constraint.count
        for actualKey, count in actualErrorCounts.items():
            if count == 0:
                continue
            actualError, level = actualKey
            if level in (ErrorLevel.SATISIFED, ErrorLevel.OK):
                continue
            diff[actualKey] = count
        return diff

    def buildResult(
            self,
            testcaseVariation: TestcaseVariation,
            actualErrors: list[ActualError],
            duration_seconds: float,
            additionalConstraints: list[tuple[str, list[TestcaseConstraint]]],
    ) -> TestcaseResult:
        actualErrorCounts: dict[tuple[str, ErrorLevel], int] = defaultdict(int)
        actualErrors, blockedErrors = self.blockCodes(actualErrors, testcaseVariation.blockedCodePattern)
        for actualError in actualErrors:
            actualErrorCounts[(actualError.code, actualError.level)] += 1
        appliedConstraints = list(testcaseVariation.testcaseConstraintSet.constraints)
        for filter, constraints in additionalConstraints:
            if fnmatch.fnmatch(testcaseVariation.fullId, f'*{filter}'):
                appliedConstraints.extend(constraints)
        appliedConstraintSet = TestcaseConstraintSet(
            constraints=self._normalizedConstraints(appliedConstraints),
            matchAll=testcaseVariation.testcaseConstraintSet.matchAll
        )
        diff = self.getDiff(appliedConstraintSet, actualErrorCounts)
        if appliedConstraintSet.matchAll or len(appliedConstraintSet.constraints) == 0: #TODO: matchAll/Any?
            # Match any vs. all operate the same when there are no constraints (valid testcase).
            passed = all(d == 0 for d in diff.values())
        else:
            passed = any(d == 0 for d in diff.values())
        constraintResults = [
            TestcaseConstraintResult(
                code=_code,
                diff=_diff,
                level=_level,
            )
            for (_code, _level), _diff in diff.items()
        ]
        return TestcaseResult(
            testcaseVariation=testcaseVariation,
            appliedConstraintSet=appliedConstraintSet,
            actualErrors=actualErrors,
            constraintResults=constraintResults,
            passed=passed,
            skip=False,
            duration_seconds=duration_seconds,
            blockedErrors=blockedErrors,
        )


    def run(self) -> list[TestcaseResult]:
        start_ts = time.perf_counter_ns()

        if self._options.logDirectory is not None:
            self._options.logDirectory.mkdir(parents=True, exist_ok=True)

        testcaseVariations = loadTestcaseIndex(self._options.indexFile, self._options)
        print(f'Loaded {len(testcaseVariations)} testcase variations from {self._options.indexFile}')
        test_realtime_ts = time.perf_counter_ns()
        if self._options.parallel:
            print('Running in parallel...')
            results = self.runTestcaseVariationsInParallel(testcaseVariations)
        else:
            print('Running in series...')
            results = self.runTestcaseVariationsInSeries(testcaseVariations)
        test_realtime_duration_seconds = (time.perf_counter_ns() - test_realtime_ts) / 1_000_000_000
        passed = sum(1 for result in results if result.passed and not result.skip)
        failed = sum(1 for result in results if not result.passed and not result.skip)
        skipped = sum(1 for result in results if result.skip)
        test_duration_seconds = sum(result.duration_seconds for result in results)
        duration_seconds = (time.perf_counter_ns() - start_ts) / 1_000_000_000
        print(
            f'Duration (seconds): '
            f'\n\tTest (Total):  \t{test_duration_seconds: .2f} (avg: {(test_duration_seconds / (len(results) or 1)): .4f})'
            f'\n\tTest (Real):  \t{test_realtime_duration_seconds: .2f} (avg: {(test_realtime_duration_seconds / (len(results) or 1)): .4f})'
            f'\n\tTotal: \t{duration_seconds: .2f}'
        )
        print(
            f'Results: '
            f'\n\tPassed: \t{passed}'
            f'\n\tFailed: \t{failed}'
            f'\n\tSkipped: \t{skipped}'
            f'\n\tTotal:  \t{len(results)}'
        )
        return results


if __name__ == "__main__":
    args = parse_args()
    testEngine = TestEngine(TestEngineOptions(
        additionalConstraints=[],
        compareFormulaOutput=False, # TODO
        customComparePatterns=[
            (expected, actual)
            for part in args.custom_compare_patterns
            for expected, sep, actual in (part.partition('|'),)
        ],
        filters=args.filters,
        ignoreLevels=frozenset(), # TODO: CLI arg
        indexFile=args.index,
        logDirectory=Path(args.log_directory) if args.log_directory else None,
        matchAll=args.match_all,
        name=None,
        options=json.loads(args.options),
        parallel=args.parallel,
    ))
    testEngine.run()
