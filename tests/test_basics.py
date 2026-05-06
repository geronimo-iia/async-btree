import pytest

from async_btree import FAILURE, SUCCESS, ControlFlowException, node_metadata

pytestmark = pytest.mark.anyio


@pytest.fixture(params=["asyncio", "trio", "asyncio+uvloop"])
def anyio_backend(request):
    backend = request.param
    if backend == "asyncio+uvloop":
        return "asyncio", {"use_uvloop": True}
    return backend, {}


def test_truthy():
    assert SUCCESS
    assert Exception()
    assert [1, 2]


def test_falsy():
    assert not []
    assert not bool([])
    assert not FAILURE
    assert not bool(FAILURE)
    assert not bool(ControlFlowException(Exception()))


def test_exception_decorator_falsy():
    assert bool(Exception())
    assert not bool(ControlFlowException(Exception()))
    assert str(ControlFlowException(Exception("test"))) == str(Exception("test"))
    assert repr(ControlFlowException(Exception("test"))) == repr(Exception("test"))


def test_exception_deduplicate():
    a = ControlFlowException(Exception("test 1"))
    b = ControlFlowException(Exception("test 2"))
    assert a != b
    assert a == ControlFlowException.instantiate(a)


async def test_node_metadata_do_not_change_behavior():
    async def a_func():
        return "a"

    assert await a_func() == "a"
    # no change on behavior
    assert await node_metadata()(a_func)() == "a"
