"""Unit tests configuration file."""

import logging

import pytest


def pytest_configure(config):
    logging.getLogger().setLevel(logging.DEBUG)
    config.addinivalue_line("markers", "all_backends: run test against all anyio backends")


@pytest.fixture
def anyio_backend(request):
    backend_name = getattr(request, "param", "asyncio")
    if backend_name == "asyncio+uvloop":
        return "asyncio", {"use_uvloop": True}
    return backend_name, {}
