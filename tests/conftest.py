"""Unit tests configuration file."""

import logging

import pytest


def pytest_configure(config):
    """Disable verbose output when running tests."""
    _logger = logging.getLogger()
    _logger.setLevel(logging.DEBUG)

    terminal = config.pluginmanager.getplugin('terminal')
    terminal.TerminalReporter.showfspath = False
