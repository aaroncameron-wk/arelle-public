"""Tests for the PluginManager module."""
from __future__ import annotations
import os
from pathlib import Path
import sys

import pytest
from unittest.mock import Mock

from arelle.PluginManager import PluginManager


def test_plugin_manager_init_first_pass():
    """
    Test that pluginConfig is correctly setup during init on fresh pass
    """
    cntlr = Mock(pluginDir='some_dir')
    pm = PluginManager(cntlr, loadPluginConfig=False)
    assert len(pm.pluginConfig) == 2
    assert 'modules' in pm.pluginConfig
    assert isinstance(pm.pluginConfig.get('modules'), dict)
    assert len(pm.pluginConfig.get('modules')) == 0
    assert 'classes' in pm.pluginConfig
    assert isinstance(pm.pluginConfig.get('classes'), dict)
    assert len(pm.pluginConfig.get('classes')) == 0
    assert len(pm.modulePluginInfos) == 0
    assert len(pm.pluginMethodsForClasses) == 0
    assert pm._cntlr == cntlr


def test_plugin_manager_init_config_already_exists():
    """
    Test that pluginConfig is correctly setup during init on a second pass
    """
    cntlr = Mock(pluginDir='some_dir')
    pm = PluginManager(cntlr, loadPluginConfig=False)
    pm.close()
    pm2 = PluginManager(cntlr, loadPluginConfig=False)
    assert len(pm2.pluginConfig) == 2
    assert 'modules' in pm2.pluginConfig
    assert isinstance(pm2.pluginConfig.get('modules'), dict)
    assert len(pm2.pluginConfig.get('modules')) == 0
    assert 'classes' in pm2.pluginConfig
    assert isinstance(pm2.pluginConfig.get('classes'), dict)
    assert len(pm2.pluginConfig.get('classes')) == 0
    assert len(pm2.modulePluginInfos) == 0
    assert len(pm2.pluginMethodsForClasses) == 0
    assert pm2._cntlr == cntlr


def test_plugin_manager_close():
    """
    Test that pluginConfig, modulePluginInfos and pluginMethodsForClasses are cleared when close is called
    """
    cntlr = Mock(pluginDir='some_dir')
    pm = PluginManager(cntlr, loadPluginConfig=False)
    assert len(pm.modulePluginInfos) == 0
    assert len(pm.pluginMethodsForClasses) == 0
    pm.modulePluginInfos['module'] = 'plugin_info'
    pm.pluginMethodsForClasses['class'] = 'plugin_method'
    pm.close()
    assert len(pm.pluginConfig) == 0
    assert len(pm.modulePluginInfos) == 0
    assert len(pm.pluginMethodsForClasses) == 0
    assert pm._cntlr == cntlr


def test_plugin_manager_reset():
    """
    Test that modulePluginInfos and pluginMethodsForClasses are cleared when reset is called, pluginConfig remains unchanged
    """
    cntlr = Mock(pluginDir='some_dir')
    pm = PluginManager(cntlr, loadPluginConfig=False)
    assert len(pm.modulePluginInfos) == 0
    assert len(pm.pluginMethodsForClasses) == 0
    pm.modulePluginInfos['module'] = 'plugin_info'
    pm.pluginMethodsForClasses['class'] = 'plugin_method'
    pm.reset()
    assert len(pm.pluginConfig) == 2
    assert len(pm.modulePluginInfos) == 0
    assert len(pm.pluginMethodsForClasses) == 0
    assert pm._cntlr == cntlr


@pytest.mark.parametrize(
    "test_data, expected_result",
    [
        # Non-existent plugin
        (
            (Path("arelle/plugin/non-existent-plugin"), "xyz"),
            (None, None, None)
        ),
        # File plugin
        (
            (Path("arelle/plugin/CacheBuilder.py"), "xyz"),
            ("CacheBuilder", "arelle/plugin", "xyz")
        ),
        # Module plugin with init file
        (
            (Path("arelle/plugin/xbrlDB/__init__.py"), "xyz"),
            ("xbrlDB", "arelle/plugin", "xbrlDB.")
        ),
        # Module plugin without init file
        (
            (Path("arelle/plugin/validate/ESEF"), "xyz"),
            ("ESEF", "arelle/plugin/validate", "ESEF.")
        ),
    ]
)
def test_function_get_name_dir_prefix(
    test_data: tuple[str, str],
    expected_result: tuple[str, str, str],
    ):
    """Test util function get_name_dir_prefix."""

    moduleName, moduleDir, packageImportPrefix = PluginManager._get_name_dir_prefix(
        modulePath=test_data[0],
        packagePrefix=test_data[1],
    )

    assert moduleName == expected_result[0]
    assert moduleDir == (None if expected_result[1] is None else os.path.normcase(expected_result[1]))
    assert packageImportPrefix == expected_result[2]


def test_function_loadModule():
    """
    Test helper function loadModule.

    This test asserts that a plugin module is loaded when running
    the function.
    """
    cntlr = Mock(pluginDir='some_dir')
    pm = PluginManager(cntlr, loadPluginConfig=False)

    pm.loadModule(
        moduleInfo={
            "name": "mock",
            "moduleURL": "functionsMath",
            "path": "arelle/plugin/functionsMath.py",
        }
    )

    all_modules_list = {m.__name__ for m in sys.modules.values() if m}

    assert "arelle.formula.XPathContext" in all_modules_list
    assert "arelle.FunctionUtil" in all_modules_list
    assert "arelle.FunctionXs" in all_modules_list
    assert "isodate.isoduration" in all_modules_list
    assert "functionsMath" in all_modules_list
