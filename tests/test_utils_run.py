import pytest
from async_btree import run, SUCCESS, FAILURE
from async_btree.utils import to_async, amap, afilter


pytestmark = pytest.mark.anyio


@pytest.fixture(
    params=["asyncio", "trio", "asyncio+uvloop"],
)
def anyio_backend(request):
    backend = request.param
    if backend == "asyncio+uvloop":
        return "asyncio", {"use_uvloop": True}
    return backend, {}


def test_run_tree_default_backend():
    async def _tree() -> bool:
        return SUCCESS

    assert run(_tree) == SUCCESS


def test_run_tree_asyncio():
    async def _tree() -> bool:
        return SUCCESS

    assert run(_tree, backend="asyncio") == SUCCESS


def test_run_tree_trio():
    async def _tree() -> bool:
        return SUCCESS

    assert run(_tree, backend="trio") == SUCCESS


def test_run_tree_uvloop():
    async def _tree() -> bool:
        return SUCCESS

    assert run(_tree, backend="asyncio+uvloop") == SUCCESS


async def test_to_async_wraps_sync():
    def sync_fn() -> bool:
        return True

    async_fn = to_async(sync_fn)
    result = await async_fn()
    assert result is True


async def test_amap():
    async def double(x: int) -> int:
        return x * 2

    result = [v async for v in amap(double, [1, 2, 3])]
    assert result == [2, 4, 6]


async def test_afilter():
    async def is_even(x: int) -> bool:
        return x % 2 == 0

    result = [v async for v in afilter(is_even, [1, 2, 3, 4])]
    assert result == [2, 4]
