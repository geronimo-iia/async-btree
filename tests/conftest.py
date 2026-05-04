"""Unit tests configuration file."""

import logging

import pytest


def pytest_configure(config):
    """Disable verbose output when running tests."""
    _logger = logging.getLogger()
    _logger.setLevel(logging.DEBUG)

    terminal = config.pluginmanager.getplugin("terminal")
    terminal.TerminalReporter.showfspath = False

    config.addinivalue_line("markers", "all_backends: run with both asyncio and curio backends")


def pytest_itemcollected(item):
    if item.get_closest_marker("all_backends"):
        item.add_marker(pytest.mark.curio, append=False)
