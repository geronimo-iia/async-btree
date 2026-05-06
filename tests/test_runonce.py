import pytest

from async_btree.utils import run_once

pytestmark = pytest.mark.anyio


@pytest.fixture(params=["asyncio", "trio", "asyncio+uvloop"])
def anyio_backend(request):
    backend = request.param
    if backend == "asyncio+uvloop":
        return "asyncio", {"use_uvloop": True}
    return backend, {}


@run_once
def inc(a: int):
    return a + 1


@run_once
async def ainc(a: int):
    return a + 1


def test_sync_runonce():
    assert inc(a=1) == 2
    assert inc(a=2) == 2


async def test_async_runonce():
    assert await ainc(a=1) == 2
    assert await ainc(a=2) == 2  # call once
