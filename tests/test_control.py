from contextvars import ContextVar

import pytest

from async_btree import (
    FAILURE,
    SUCCESS,
    ControlFlowException,
    decision,
    fallback,
    ignore_exception,
    repeat_until,
    selector,
    sequence,
)


async def a_func():
    return "a"


async def b_func():
    return "b"


async def failure_func():
    return FAILURE


async def success_func():
    return SUCCESS


async def exception_func():
    raise RuntimeError("ops")


@pytest.mark.curio
async def test_sequence():
    assert not await sequence(children=[a_func, failure_func, success_func])(), "default behaviour fail of one failed"

    assert await sequence(children=[a_func, failure_func, success_func], succes_threshold=2)()
    assert await sequence(children=[a_func, success_func, failure_func], succes_threshold=2)()
    assert await sequence(children=[failure_func, a_func, success_func], succes_threshold=2)(), (
        "must continue after first failure"
    )

    with pytest.raises(RuntimeError):
        assert await sequence(children=[exception_func, failure_func, a_func], succes_threshold=1)()

    with pytest.raises(RuntimeError):
        assert not await sequence(children=[failure_func, exception_func], succes_threshold=1)()

    assert not await sequence(children=[])()
    # negative
    with pytest.raises(AssertionError):
        sequence(children=[exception_func, failure_func], succes_threshold=-2)
    # upper than len children
    with pytest.raises(AssertionError):
        sequence(children=[exception_func, failure_func], succes_threshold=3)

    meta = sequence(children=[]).__node_metadata
    assert meta.name == "sequence"
    assert "_succes_threshold" in meta.properties


@pytest.mark.curio
async def test_fallback():
    with pytest.raises(RuntimeError):
        assert await fallback(children=[exception_func, failure_func, a_func])()
    assert await fallback(children=[a_func, failure_func])() == ["a"]
    assert not await fallback(children=[])()
    assert fallback(children=[]).__node_metadata.name == "fallback"


@pytest.mark.curio
async def test_selector():
    with pytest.raises(RuntimeError):
        assert await selector(children=[exception_func, failure_func, a_func])()
    assert await selector(children=[a_func, failure_func])() == ["a"]
    assert selector(children=[]).__node_metadata.name == "selector"


@pytest.mark.curio
async def test_decision():
    assert await decision(condition=success_func, success_tree=a_func)() == "a"
    # return SUCCESS when no failure_tree and False condition result
    assert await decision(condition=failure_func, success_tree=a_func)()

    result = await decision(condition=failure_func, success_tree=a_func, failure_tree=b_func)()
    assert result == "b", "failure tree must be called"

    meta = decision(condition=failure_func, success_tree=a_func).__node_metadata
    assert meta.name == "decision"
    for key in ["_condition", "_success_tree", "_failure_tree"]:
        assert key in meta.edges


@pytest.mark.curio
async def test_repeat_until_falsy_condition():
    counter = ContextVar("counter", default=5)

    async def tick():
        value = counter.get()
        counter.set(value - 1)
        if value <= 0:
            return FAILURE
        if value == 3:
            raise RuntimeError("3")
        return SUCCESS

    assert await repeat_until(condition=ignore_exception(tick), child=a_func)() == "a", "return last sucess result"
    assert counter.get() == 2

    meta = repeat_until(condition=ignore_exception(tick), child=a_func).__node_metadata
    assert meta.name == "repeat_until"
    for key in ["_condition", "_child"]:
        assert key in meta.edges


@pytest.mark.curio
async def test_repeat_until_return_last_result():
    counter = ContextVar("tick_test_repeat_until_return_last_result", default=5)

    async def tick():
        value = counter.get()
        counter.set(value - 1)
        if value <= 0:
            return FAILURE
        return SUCCESS

    result = await repeat_until(condition=tick, child=ignore_exception(exception_func))()
    assert counter.get() == -1
    assert isinstance(result, ControlFlowException)
