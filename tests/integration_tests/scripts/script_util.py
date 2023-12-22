from __future__ import annotations

import argparse
import os
import shlex
import shutil
import subprocess
import sys
from os import linesep
from pathlib import Path
from typing import cast, Iterable, Any

from lxml import etree

from tests.integration_tests.download_cache import download_and_apply_cache


def assert_result(errors: list[str]) -> None:
    assert len(errors) == 0, f"Errors encountered during test:\n{linesep.join(errors)}"


def cleanup(
        working_directory: Path,
        paths: list[Path]
) -> None:
    for path in paths:
        assert working_directory in path.parents, \
            f'Attempted to cleanup directory "{path}" not within working directory "{working_directory}"'
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()


def parse_args(
    name: str,
    description: str,
    arelle: bool = True,
    cache: str | None = None,
    working_directory: bool = True,
) -> argparse.Namespace:
    """
    Parses standard integration test script arguments and returns the results
    after some preprocessing based on values.
    :param name: Name of the test. Note that this is used in the default working directory path.
    :param description: Human-readable description of the test.
    :param arelle: Whether '--arelle' argument is required.
    :param cache: Name of the cache that will be downloaded if `--download-cache` is provided.
    :param working_directory: Whether a working directory should be configured.
    :return: Parsed argument Namespace.
    """
    parser = argparse.ArgumentParser(prog=name, description=description)
    parser.add_argument("--arelle", action="store", required=arelle,
                        help="CLI command to run Arelle.")
    parser.add_argument("--download-cache", action="store_true",
                        help=f"Whether or not to download and apply cache.")
    parser.add_argument("--offline", action="store_true",
                        help="True if Arelle should run in offline mode.")
    parser.add_argument("--working-directory", action="store", default=".test",
                        help="Directory to place temporary files and log output.")
    parsed_args = parser.parse_args()
    if cache and parsed_args.download_cache:
        download_and_apply_cache(f"scripts/{cache}")
        print(f"Downloaded and applied cache: {cache}")
    if working_directory:
        directory = Path(parsed_args.working_directory).joinpath(name).absolute()
        parsed_args.working_directory = directory
        directory.mkdir(parents=True, exist_ok=True)
        print(f"Set working directory: {directory}")
    return parsed_args


def prepare_logfile(working_directory: Path, script_path: Path, name: str | None = None) -> Path:
    name_part = "" if name is None else f".{name}"
    logfile_path = working_directory.joinpath(script_path.stem).with_suffix(f"{name_part}.logfile.xml")
    logfile_path.unlink(missing_ok=True)
    return logfile_path


def run_arelle(
    arelle_command: str,
    plugins: list[str] | None = None,
    additional_args: list[str] | None = None,
    offline: bool = False,
    logFile: Path | None = None,
) -> None:
    if os.name == 'nt':
        args = [sys.executable if w == 'python' else w for w in arelle_command.split()]
    else:
        args = shlex.split(arelle_command)
    if plugins:
        args.append(f"--plugins={'|'.join(plugins)}")
    if offline:
        args.append("--internetConnectivity=offline")
    args.extend(additional_args or [])
    if logFile:
        args.extend(["--logFile", str(logFile)])
    if os.name == 'nt':
        result = subprocess.run(args, capture_output=True, shell=True)
    else:
        result = subprocess.run(args, capture_output=True)
    assert result.returncode == 0, result.stderr.decode().strip()


def validate_log_file(
    logfile_path: Path
) -> list[str]:
    if not logfile_path.exists():
        return [f'Log file "{logfile_path}" not found.']
    tree = etree.parse(logfile_path)
    matches = cast(Iterable[Any], tree.xpath("//log/entry[@level='error']/message/text()"))
    return [str(x) for x in matches]
