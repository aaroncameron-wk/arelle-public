from __future__ import annotations

import fnmatch
import json
import os as os_module
import re
from typing import TypedDict, Iterable

import sys

from .conformance_suite_config import ConformanceSuiteConfig
from .conformance_suite_configs import CI_CONFORMANCE_SUITE_CONFIGS
from .conformance_suite_configurations.efm_current import config as efm_current
from .conformance_suite_configurations.xbrl_2_1 import config as xbrl_2_1


LINUX = 'ubuntu-24.04'
MACOS = 'macos-15'
WINDOWS = 'windows-2022'
ALL_PYTHON_VERSIONS = (
    '3.9',
    '3.10',
    '3.11',
    '3.12',
    '3.13.5',
)
LATEST_PYTHON_VERSION = '3.13.5'
# number of cores on the runners
# https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners/about-github-hosted-runners#supported-runners-and-hardware-resources
OS_CORES = {
    LINUX: 4,
    MACOS: 3,
    WINDOWS: 4,
}
FAST_CONFIG_NAMES = {
    'esef_xhtml_2021',
    'esef_xhtml_2022',
    'esef_xhtml_2023',
    'esef_xhtml_2024',
    'xbrl_calculations_1_1',
    'xbrl_dimensions_1_0',
    'xbrl_dtr_2024_01_31',
    'xbrl_extensible_enumerations_1_0',
    'xbrl_extensible_enumerations_2_0',
    'xbrl_formula_1_0_assertion_severity_2_0',
    'xbrl_formula_1_0_function_registry',
    'xbrl_link_role_registry_1_0',
    'xbrl_oim_1_0',
    'xbrl_report_packages_1_0',
    'xbrl_taxonomy_packages_1_0',
    'xbrl_transformation_registry_3',
    'xbrl_utr_malformed_1_0',
    'xbrl_utr_registry_1_0',
    'xbrl_utr_structure_1_0',
}


class Entry(TypedDict, total=False):
    environment: str
    name: str
    short_name: str
    os: str
    python_version: str
    shard: str


def generate_config_entry(name: str, short_name: str, os: str, private: bool, python_version: str, shard: str | None) -> Entry:
    e: Entry = {
        'environment': 'integration-tests' if private else 'none',
        'name': name,
        'short_name': short_name,
        'os': os,
        'python_version': python_version,
    }
    if shard is not None:
        e['shard'] = shard
    return e


def generate_config_entries(config: ConformanceSuiteConfig, os: str, python_version: str, minimal: bool = False) -> Iterable[Entry]:
    if config.shards == 1:
        yield generate_config_entry(
            name=config.name,
            short_name=config.name,
            os=os,
            private=config.has_private_asset,
            python_version=python_version,
            shard=None,
        )
    else:
        ncores = OS_CORES[os]
        shard_range = [0] if minimal else range(0, config.shards, ncores)
        for start in shard_range:
            end = min(config.shards, start + ncores) - 1
            yield generate_config_entry(
                name=config.name,
                short_name=config.name,
                os=os,
                private=config.has_private_asset,
                python_version=python_version,
                shard=f'{start}-{end}',
            )


def _skip_config(name: str, patterns: list[str]) -> bool:
    if patterns and not any(fnmatch.fnmatch(name, pattern) for pattern in patterns):
        return True
    return False


def _get_pr_body_filters() -> list[str]:
    event_path = os_module.getenv("GITHUB_EVENT_PATH")
    if not event_path:
        return []
    with open(event_path, "r") as f:
        event = json.load(f)
        body = event["pull_request"]["body"]
        print(f'Parsing PR body for filters: [[[{body}]]]')
        return re.findall(r'CONFORMANCE_SUITE_FILTER\((.*)\)', body)



def main() -> None:
    patterns = _get_pr_body_filters()
    if patterns:
        print(f'Using filters: {patterns}')
    filtered_configs = [
        config for config in CI_CONFORMANCE_SUITE_CONFIGS
        if not _skip_config(config.name, patterns)
    ]
    filtered_fast_config_names = [
        name for name in FAST_CONFIG_NAMES
        if not _skip_config(name, patterns)
    ]

    output: list[Entry] = []
    config_names_seen: set[str] = set()
    private = False
    if not patterns:
        for config in filtered_configs:
            if config.name in filtered_fast_config_names:
                assert not config.network_or_cache_required
                assert config.shards == 1
                config_names_seen.add(config.name)
                private |= config.has_private_asset
        assert not (filtered_fast_config_names - config_names_seen), \
            f'Missing some fast configurations: {sorted(filtered_fast_config_names - config_names_seen)}'
        for os in [LINUX, MACOS, WINDOWS]:
            output.append(generate_config_entry(
                name=','.join(sorted(filtered_fast_config_names)),
                short_name='miscellaneous suites',
                os=os,
                private=private,
                python_version=LATEST_PYTHON_VERSION,
                shard=None,
            ))

    for config in filtered_configs:
        # configurations don't necessarily have unique names, e.g. malformed UTR
        if config.name in config_names_seen:
            continue
        if patterns and not any(fnmatch.fnmatch(config.name, pattern) for pattern in patterns):
            continue
        config_names_seen.add(config.name)
        output.extend(generate_config_entries(config, os=LINUX, python_version=LATEST_PYTHON_VERSION))
    if not _skip_config(xbrl_2_1.name, patterns):
        for os in [LINUX, MACOS, WINDOWS]:
            for python_version in ALL_PYTHON_VERSIONS:
                if os == LINUX and python_version == LATEST_PYTHON_VERSION:
                    continue
                output.extend(generate_config_entries(xbrl_2_1, os=os, python_version=python_version))
    if not _skip_config(efm_current.name, patterns):
        for os in [MACOS, WINDOWS]:
            output.extend(generate_config_entries(efm_current, os=os, python_version=LATEST_PYTHON_VERSION, minimal=True))

    json.dump(output, sys.stdout, indent=4)
    print()


if __name__ == '__main__':
    main()
