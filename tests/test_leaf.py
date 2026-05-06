import pytest

from async_btree import action, condition, ignore_exception

pytestmark = pytest.mark.anyio


@pytest.fixture(params=["asyncio", "trio", "asyncio+uvloop"])
def anyio_backend(request):
    backend = request.param
    if backend == "asyncio+uvloop":
        return "asyncio", {"use_uvloop": True}
    return backend, {}


async def test_condition():
    async def target_test(value):
        return value

    assert await condition(target_test, value=True)()  # pylint: disable=unexpected-keyword-arg

    assert not await condition(target_test, value=False)()  # pylint: disable=unexpected-keyword-arg
    assert condition(target_test, value=False).__node_metadata.name == "condition"
    assert "target" in condition(target_test, value=False).__node_metadata.properties


async def test_action_with_exception_is_falsy():
    async def generate_exception():
        raise Exception("Bing!")

    assert not await ignore_exception(action(generate_exception))()


async def test_action_results():
    async def compute(a, b):
        return a + b

    assert await action(compute, a=1, b=1)() == 2
    assert action(compute, a=1, b=1).__node_metadata.name == "action"
