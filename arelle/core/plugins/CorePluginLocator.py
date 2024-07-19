"""
See COPYRIGHT.md for copyright information.
"""
from __future__ import annotations

import os
import sys
from collections import defaultdict
from importlib.metadata import EntryPoint, entry_points
from typing import TYPE_CHECKING

from arelle.services.plugins.EntryPointRef import EntryPointRef
from arelle.services.plugins.PluginLocator import PluginLocator
from arelle.services.plugins.PluginParser import PluginParser

if TYPE_CHECKING:
    from arelle.Cntlr import Cntlr

_CACHE: list[EntryPointRef] | None = None
_ALIAS_CACHE: dict[str, list[EntryPointRef]] | None = None
_SEARCH_TERM_ENDINGS = [
    '/__init__.py',
    '.py'
    '/'
]


class CorePluginLocator(PluginLocator):

    def __init__(self, controller: Cntlr, plugin_parser: PluginParser):
        self._controller = controller
        self._plugin_parser = plugin_parser

    def _discover_all(self, plugin_base: str) -> list[EntryPointRef]:
        """
        Retrieve all plugin entry points, cached on first run.
        :return: List of all discovered entry points.
        """
        global _CACHE
        if _CACHE is None:
            _CACHE = \
                self._discover_built_in([], plugin_base) + \
                self._discover_installed()
        return _CACHE

    def _discover_built_in(self, entryPointRefs: list[EntryPointRef], directory: str) -> list[EntryPointRef]:
        """
        Recursively retrieve all plugin entry points in the given directory.
        :param entryPointRefs: Working list of entry point refs to append to.
        :param directory: Directory to search for entry points within.
        :return: List of discovered entry points.
        """
        for fileName in sorted(os.listdir(directory)):
            if fileName in (".", "..", "__pycache__", "__init__.py", ".DS_Store", "site-packages"):
                continue  # Ignore these entries
            filePath = os.path.join(directory, fileName)
            if os.path.isdir(filePath):
                self._discover_built_in(entryPointRefs, filePath)
            if os.path.isfile(filePath) and os.path.basename(filePath).endswith(".py"):
                # If `filePath` references .py file directly, use it
                moduleFilePath = filePath
            elif os.path.isdir(filePath) and os.path.exists(initFilePath := os.path.join(filePath, "__init__.py")):
                # Otherwise, if `filePath` is a directory containing `__init__.py`, use that
                moduleFilePath = initFilePath
            else:
                continue
            entryPointRef = self._from_filepath(moduleFilePath)
            if entryPointRef is not None:
                entryPointRefs.append(entryPointRef)
        return entryPointRefs

    def _discover_installed(self) -> list[EntryPointRef]:
        """
        Retrieve all installed plugin entry points.
        :return:
        :return: List of all discovered entry points.
        """
        entryPoints: list[EntryPoint]
        if sys.version_info < (3, 10):
            entryPoints = [e for e in entry_points().get('arelle.plugin', [])]
        else:
            entryPoints = list(entry_points(group='arelle.plugin'))
        entryPointRefs = []
        for entryPoint in entryPoints:
            entryPointRef = self._from_entry_point(entryPoint)
            if entryPointRef is not None:
                entryPointRefs.append(entryPointRef)
        return entryPointRefs

    def _from_filepath(self, filepath: str, entryPoint: EntryPoint | None = None) -> EntryPointRef | None:
        """
        Given a filepath, retrieves a subset of information from __pluginInfo__ necessary to
        determine if the entry point should be imported as a plugin.
        :param filepath: Path to plugin, can be a directory or .py filepath
        :param entryPoint: Optional entry point information to include in aliases/moduleInfo
        :return:
        """
        moduleFilename = self._controller.webCache.getfilename(filepath)
        if moduleFilename:
            moduleFilename = self.normalize_module_filename(moduleFilename)
        aliases = set()
        if entryPoint:
            aliases.add(entryPoint.name)
        moduleInfo: dict | None = None
        if moduleFilename:
            moduleInfo = self._plugin_parser.parse_plugin_info(moduleFilename, moduleFilename, entryPoint)
            if moduleInfo is None:
                return None
            if "name" in moduleInfo:
                aliases.add(moduleInfo["name"])
            if "aliases" in moduleInfo:
                aliases |= set(moduleInfo["aliases"])
        return EntryPointRef(
            aliases={CorePluginLocator._normalize_plugin_search_term(a) for a in aliases},
            entryPoint=entryPoint,
            moduleFilename=moduleFilename,
            moduleInfo=moduleInfo,
        )

    def _from_entry_point(self, entryPoint: EntryPoint) -> EntryPointRef | None:
        """
        Given an entry point, retrieves the subset of information from __pluginInfo__ necessary to
        determine if the entry point should be imported as a plugin.
        :param entryPoint:
        :return:
        """
        pluginUrlFunc = entryPoint.load()
        pluginUrl = pluginUrlFunc()
        return self._from_filepath(pluginUrl, entryPoint)

    def _search(self, plugin_base: str, search: str) -> list[EntryPointRef] | None:
        """
        Retrieve entry point module information matching provided search text.
        A map of aliases to matching entry points is cached on the first run.
        :param search: Only retrieve entry points matching the given search text.
        :return: List of matching module infos.
        """
        global _ALIAS_CACHE
        if _ALIAS_CACHE is None:
            entryPointRefAliasCache = defaultdict(list)
            entryPointRefs = self._discover_all(plugin_base)
            for entryPointRef in entryPointRefs:
                for alias in entryPointRef.aliases:
                    entryPointRefAliasCache[alias].append(entryPointRef)
            _ALIAS_CACHE = entryPointRefAliasCache
        search = CorePluginLocator._normalize_plugin_search_term(search)
        return _ALIAS_CACHE.get(search, [])

    def normalize_module_filename(self, moduleFilename: str) -> str | None:
        """
        Attempts to find python script as plugin entry point.
        A value will be returned
          if `moduleFilename` exists as-is,
          if `moduleFilename` is a directory containing __init__.py, or
          if `moduleFilename` with .py extension added exists
        :param moduleFilename:
        :return: Normalized filename, if exists
        """
        if os.path.isfile(moduleFilename):
            # moduleFilename exists as-is, use it
            return moduleFilename
        if os.path.isdir(moduleFilename):
            # moduleFilename is a directory, only valid script is __init__.py contained inside
            initPath = os.path.join(moduleFilename, "__init__.py")
            if os.path.isfile(initPath):
                return initPath
            else:
                return None
        if not moduleFilename.endswith(".py"):
            # moduleFilename is not a file or directory, try adding .py
            pyPath = moduleFilename + ".py"
            if os.path.exists(pyPath):
                return pyPath
        return None

    @staticmethod
    def _normalize_plugin_search_term(search: str) -> str:
        """
        Normalizes the given search term or searchable text by:
          Making slashes consistent
          Removing common endings
        :param search: Search term or searchable text
        :return: Normalized string
        """
        search = search.replace('\\', '/')
        while True:
            for ending in _SEARCH_TERM_ENDINGS:
                if search.endswith(ending):
                    search = search[:-len(ending)]
                    break
            return search.lower()

    def get(self, plugin_base: str, search: str) -> EntryPointRef | None:
        """
        Retrieve an entry point ref with a matching name or alias.
        May return None of no matches are found.
        Throws an exception if multiple entry point refs match the search term.
        :param search: Only retrieve entry point matching the given search text.
        :return: Matching entry point ref, if found.
        """
        entryPointRefs = self._search(plugin_base, search)
        if len(entryPointRefs) == 0:
            return None
        elif len(entryPointRefs) > 1:
            paths = [r.moduleFilename for r in entryPointRefs]
            raise Exception(_('Multiple entry points matched search term "{}": {}').format(search, paths))
        return entryPointRefs[0]
