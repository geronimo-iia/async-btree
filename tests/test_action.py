import pytest

from async_btree import ControlFlowException, action

pytestmark = pytest.mark.anyio


@pytest.fixture(params=["asyncio", "trio", "asyncio+uvloop"])
def anyio_backend(request):
    backend = request.param
    if backend == "asyncio+uvloop":
        return "asyncio", {"use_uvloop": True}
    return backend, {}


async def test_action_result_with_exceptions():
    def div_zero():
        return 1 / 0

    fn = action(target=div_zero)
    assert fn
    with pytest.raises(ControlFlowException):
        await fn()

    assert fn.__node_metadata.name == "action"
    assert "_target" in fn.__node_metadata.properties
