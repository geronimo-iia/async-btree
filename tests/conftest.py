"""Unit tests configuration file."""

import logging

import pytest


def pytest_configure(config):
    logging.getLogger().setLevel(logging.DEBUG)
    config.addinivalue_line("markers", "all_backends: run test against all anyio backends")


def pytest_collection_modifyitems(items):
    try:
        import uvloop  # noqa: F401
    except ImportError:
        skip = pytest.mark.skip(reason="uvloop not available on this Python version")
        for item in items:
            if hasattr(item, "callspec") and item.callspec.params.get("anyio_backend") == "asyncio+uvloop":
                item.add_marker(skip)


@pytest.fixture
def anyio_backend(request):
    backend_name = getattr(request, "param", "asyncio")
    if backend_name == "asyncio+uvloop":
        return "asyncio", {"use_uvloop": True}
    return backend_name, {}
