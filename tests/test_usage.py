import pytest

from async_btree import FAILURE, SUCCESS, decision

pytestmark = pytest.mark.anyio


@pytest.fixture(params=["asyncio", "trio", "asyncio+uvloop"])
def anyio_backend(request):
    backend = request.param
    if backend == "asyncio+uvloop":
        return "asyncio", {"use_uvloop": True}
    return backend, {}


async def i_fail():
    return FAILURE


async def some_action():
    print("continue here...")
    return SUCCESS


async def test_usage():
    tree = decision(condition=i_fail, success_tree=some_action, failure_tree=lambda: 42)

    assert await tree() == 42
