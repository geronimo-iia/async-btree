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


def test_node_metadata_do_not_change_behavior(kernel):
    async def a_func():
        return 'a'

    assert kernel.run(a_func) == 'a'
    # no change on behavior
    assert kernel.run(node_metadata()(a_func)) == 'a'
