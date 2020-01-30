from contextvars import ContextVar

import pytest

from async_btree import FAILURE, SUCCESS, ExceptionDecorator, decision, fallback, repeat_until, selector, sequence


async def a_func():
    return 'a'


async def b_func():
    return 'b'


async def failure_func():
    return FAILURE


async def success_func():
    return SUCCESS


async def exception_func():
    raise RuntimeError("ops")


def test_sequence(kernel):
    assert not kernel.run(
        sequence(children=[a_func, failure_func, success_func])
    ), "default behaviour fail of one failed"

    assert kernel.run(sequence(children=[a_func, failure_func, success_func], succes_threshold=2))
    assert kernel.run(sequence(children=[a_func, success_func, failure_func], succes_threshold=2))
    assert kernel.run(
        sequence(children=[failure_func, a_func, success_func], succes_threshold=2)
    ), 'must continue after first failure'

    assert kernel.run(sequence(children=[exception_func, failure_func, a_func], succes_threshold=1))
    assert not kernel.run(sequence(children=[exception_func, failure_func], succes_threshold=1))

    assert not kernel.run(sequence(children=[]))
    # negative
    with pytest.raises(AssertionError):
        sequence(children=[exception_func, failure_func], succes_threshold=-2)
    # upper than len children
    with pytest.raises(AssertionError):
        sequence(children=[exception_func, failure_func], succes_threshold=3)


def test_fallback(kernel):
    assert kernel.run(fallback(children=[exception_func, failure_func, a_func]))
    assert not kernel.run(fallback(children=[exception_func, failure_func]))
    assert not kernel.run(fallback(children=[]))


def test_selector(kernel):
    assert kernel.run(selector(children=[exception_func, failure_func, a_func]))
    assert not kernel.run(selector(children=[exception_func, failure_func]))
    assert selector(children=[]).__node_metadata.name == 'selector'


def test_decision(kernel):
    assert kernel.run(decision(condition=success_func, success_tree=a_func)) == 'a'
    assert not kernel.run(decision(condition=failure_func, success_tree=a_func))

    result = kernel.run(decision(condition=failure_func, success_tree=a_func, failure_tree=b_func))
    assert result == 'b', 'failure tree must be called'


def test_repeat_until_falsy_condition(kernel):

    counter = ContextVar('counter', default=5)

    async def tick():
        value = counter.get()
        counter.set(value - 1)
        if value <= 0:
            return FAILURE
        if value == 3:
            raise RuntimeError('3')
        return SUCCESS

    assert kernel.run(repeat_until(condition=tick, child=a_func)) == 'a', 'return last sucess result'
    assert counter.get() == 2


def test_repeat_until_return_last_result(kernel):

    counter = ContextVar('tick_test_repeat_until_return_last_result', default=5)

    async def tick():
        value = counter.get()
        counter.set(value - 1)
        if value <= 0:
            return FAILURE
        return SUCCESS

    result = kernel.run(repeat_until(condition=tick, child=exception_func))
    assert counter.get() == -1
    assert isinstance(result, ExceptionDecorator)
