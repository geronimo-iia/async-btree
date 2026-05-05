import pytest

from async_btree import afilter, amap

pytestmark = pytest.mark.anyio


@pytest.fixture(params=["asyncio", "trio", "asyncio+uvloop"])
def anyio_backend(request):
    backend = request.param
    if backend == "asyncio+uvloop":
        return "asyncio", {"use_uvloop": True}
    return backend, {}


async def inc(a):
    return a + 1


async def even(a):
    return a % 2 == 0


async def test_amap_on_iterable():
    async def process():
        return [i async for i in amap(inc, [1, 2])]

    assert await process() == [2, 3]


async def test_afilter_on_iterable():
    async def process():
        return [i async for i in afilter(even, [0, 1, 2, 3, 4])]

    assert await process() == [0, 2, 4]


async def test_afilter_amap_aiter():
    async def process1():
        return [i async for i in afilter(even, amap(inc, [0, 1, 2, 3, 4]))]

    async def process2():
        return [i async for i in amap(inc, afilter(even, [0, 1, 2, 3, 4]))]

    assert await process1() == [2, 4]
    assert await process2() == [1, 3, 5]
