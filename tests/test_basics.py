import pytest

from async_btree import FAILURE, SUCCESS, ExceptionDecorator, node_metadata


def test_truthy():
    assert SUCCESS
    assert Exception()
    assert [1, 2]


def test_falsy():
    assert not []
    assert not bool([])
    assert not FAILURE
    assert not bool(FAILURE)
    assert not bool(ExceptionDecorator(Exception()))


def test_exception_decorator_falsy():
    assert bool(Exception())
    assert not bool(ExceptionDecorator(Exception()))
    assert str(ExceptionDecorator(Exception("test"))) == str(Exception("test"))
    assert repr(ExceptionDecorator(Exception("test"))) == repr(Exception("test"))


@pytest.mark.curio
async def test_node_metadata_do_not_change_behavior():
    async def a_func():
        return 'a'

    assert await a_func() == 'a'
    # no change on behavior
    assert await node_metadata()(a_func)() == 'a'
