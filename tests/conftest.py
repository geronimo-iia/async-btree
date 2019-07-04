"""Unit tests configuration file."""

import logging

import pytest
from curio import Kernel
from curio.debug import logcrash, longblock
from curio.monitor import Monitor


@pytest.fixture(scope='session')
def kernel(request):
    k = Kernel(debug=[longblock, logcrash])
    m = Monitor(k)
    request.addfinalizer(lambda: k.run(shutdown=True))
    request.addfinalizer(m.close)
    return k


def pytest_configure(config):
    """Disable verbose output when running tests."""
    _logger = logging.getLogger()
    _logger.setLevel(logging.DEBUG)

    terminal = config.pluginmanager.getplugin('terminal')
    terminal.TerminalReporter.showfspath = False


def run(corofunc, *args):

    kernel().run(corofunc, *args)
