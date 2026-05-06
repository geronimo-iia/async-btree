from contextvars import ContextVar

import pytest

from async_btree import (
    FAILURE,
    SUCCESS,
    ControlFlowException,
    condition_guard,
    decision,
    do_while,
    fallback,
    ignore_exception,
    random_selector,
    repeat_n,
    repeat_until,
    repeat_while,
    selector,
    sequence,
    switch,
)

pytestmark = pytest.mark.anyio


@pytest.fixture(params=["asyncio", "trio", "asyncio+uvloop"])
def anyio_backend(request):
    backend = request.param
    if backend == "asyncio+uvloop":
        return "asyncio", {"use_uvloop": True}
    return backend, {}


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


async def test_sequence():
    assert not await sequence(children=[a_func, failure_func, success_func])(), "default behaviour fail of one failed"

    assert await sequence(children=[a_func, failure_func, success_func], success_threshold=2)()
    assert await sequence(children=[a_func, success_func, failure_func], success_threshold=2)()
    assert await sequence(children=[failure_func, a_func, success_func], success_threshold=2)(), (
        "must continue after first failure"
    )

    with pytest.raises(RuntimeError):
        assert await sequence(children=[exception_func, failure_func, a_func], success_threshold=1)()

    with pytest.raises(RuntimeError):
        assert not await sequence(children=[failure_func, exception_func], success_threshold=1)()

    assert not await sequence(children=[])()
    # negative
    with pytest.raises(AssertionError):
        sequence(children=[exception_func, failure_func], success_threshold=-2)
    # upper than len children
    with pytest.raises(AssertionError):
        sequence(children=[exception_func, failure_func], success_threshold=3)

    meta = sequence(children=[]).__node_metadata
    assert meta.name == "sequence"
    assert "_success_threshold" in meta.properties


async def test_fallback():
    with pytest.raises(RuntimeError):
        assert await fallback(children=[exception_func, failure_func, a_func])()
    assert await fallback(children=[a_func, failure_func])() == ["a"]
    assert not await fallback(children=[])()
    assert fallback(children=[]).__node_metadata.name == "fallback"


async def test_selector():
    with pytest.raises(RuntimeError):
        assert await selector(children=[exception_func, failure_func, a_func])()
    assert await selector(children=[a_func, failure_func])() == ["a"]
    assert selector(children=[]).__node_metadata.name == "selector"


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


async def test_repeat_while_truthy_condition():
    counter = ContextVar("counter", default=5)

    async def tick():
        value = counter.get()
        counter.set(value - 1)
        if value <= 0:
            return FAILURE
        if value == 3:
            raise RuntimeError("3")
        return SUCCESS

    assert await repeat_while(condition=ignore_exception(tick), child=a_func)() == "a", "return last success result"
    assert counter.get() == 2

    meta = repeat_while(condition=ignore_exception(tick), child=a_func).__node_metadata
    assert meta.name == "repeat_while"
    for key in ["_condition", "_child"]:
        assert key in meta.edges


async def test_repeat_while_return_last_result():
    counter = ContextVar("tick_test_repeat_while_return_last_result", default=5)

    async def tick():
        value = counter.get()
        counter.set(value - 1)
        if value <= 0:
            return FAILURE
        return SUCCESS

    result = await repeat_while(condition=tick, child=ignore_exception(exception_func))()
    assert counter.get() == -1
    assert isinstance(result, ControlFlowException)


async def test_repeat_until_truthy_condition():
    # condition starts falsy, becomes truthy after N ticks → child runs N times
    counter = ContextVar("counter_repeat_until", default=0)

    async def tick():
        value = counter.get()
        counter.set(value + 1)
        return value >= 3  # truthy when counter reaches 3

    result = await repeat_until(condition=tick, child=a_func)()
    assert result == "a", "returns last child result"
    assert counter.get() == 4  # called 4 times: 0,1,2 falsy → run child; 3 truthy → stop

    meta = repeat_until(condition=tick, child=a_func).__node_metadata
    assert meta.name == "repeat_until"
    for key in ["_condition", "_child"]:
        assert key in meta.edges


async def test_repeat_until_immediate_truthy():
    # condition truthy on first check → no iteration, returns FAILURE
    async def always_true():
        return SUCCESS

    result = await repeat_until(condition=always_true, child=a_func)()
    assert result is FAILURE


async def test_condition_guard_truthy():
    ran = []

    async def cond():
        return SUCCESS

    async def child():
        ran.append(1)
        return "done"

    result = await condition_guard(condition=cond, child=child)()
    assert result == "done"
    assert ran == [1]


async def test_condition_guard_falsy():
    ran = []

    async def cond():
        return FAILURE

    async def child():
        ran.append(1)
        return "done"

    result = await condition_guard(condition=cond, child=child)()
    assert result is SUCCESS
    assert ran == []


async def test_condition_guard_metadata():
    async def cond():
        return SUCCESS

    async def child():
        return SUCCESS

    meta = condition_guard(condition=cond, child=child).__node_metadata
    assert meta.name == "condition_guard"


async def test_do_while_runs_at_least_once():
    ran = []

    async def child():
        ran.append(1)
        return "done"

    async def never():
        return FAILURE

    result = await do_while(child=child, condition=never)()
    assert result == "done"
    assert len(ran) == 1


async def test_do_while_repeats_while_truthy():
    runs = ContextVar("runs_do_while", default=0)
    ticks = ContextVar("ticks_do_while", default=3)

    async def child():
        runs.set(runs.get() + 1)
        return runs.get()

    async def condition():
        v = ticks.get()
        ticks.set(v - 1)
        return v > 0  # truthy for first 3 checks, then falsy

    await do_while(child=child, condition=condition)()
    assert runs.get() == 4  # ran once before first check + 3 more while truthy


async def test_do_while_metadata():
    async def child():
        return SUCCESS

    async def cond():
        return FAILURE

    meta = do_while(child=child, condition=cond).__node_metadata
    assert meta.name == "do_while"
    assert "_child" in meta.edges
    assert "_condition" in meta.edges


async def test_repeat_n_runs_exactly_n_times():
    counter = ContextVar("counter_repeat_n", default=0)

    async def child():
        counter.set(counter.get() + 1)
        return counter.get()

    result = await repeat_n(child=child, n=4)()
    assert result == 4
    assert counter.get() == 4


async def test_repeat_n_zero():
    result = await repeat_n(child=a_func, n=0)()
    assert result is FAILURE


async def test_repeat_n_metadata():
    meta = repeat_n(child=a_func, n=3).__node_metadata
    assert meta.name == "repeat_n"
    assert "n" in meta.properties


async def test_random_selector_succeeds_on_first_truthy():
    results = []

    async def child_a():
        results.append("a")
        return SUCCESS

    async def child_b():
        results.append("b")
        return SUCCESS

    result = await random_selector(children=[child_a, child_b])()
    assert result  # truthy
    assert len(results) == 1  # stopped at first success


async def test_random_selector_tries_all_on_failure():
    async def fail_a():
        return FAILURE

    async def fail_b():
        return FAILURE

    result = await random_selector(children=[fail_a, fail_b])()
    assert result is FAILURE


async def test_random_selector_metadata():
    meta = random_selector(children=[a_func, success_func]).__node_metadata
    assert meta.name == "random_selector"


async def test_switch_matches_case():
    async def get_key():
        return "b"

    async def child_a():
        return "A"

    async def child_b():
        return "B"

    result = await switch(condition=get_key, cases={"a": child_a, "b": child_b})()
    assert result == "B"


async def test_switch_no_match_no_default():
    async def get_key():
        return "x"

    async def child_a():
        return "A"

    result = await switch(condition=get_key, cases={"a": child_a})()
    assert result is FAILURE


async def test_switch_no_match_with_default():
    async def get_key():
        return "x"

    async def child_a():
        return "A"

    async def default_child():
        return "default"

    result = await switch(condition=get_key, cases={"a": child_a}, default=default_child)()
    assert result == "default"


async def test_switch_metadata():
    async def get_key():
        return "a"

    async def child_a():
        return SUCCESS

    meta = switch(condition=get_key, cases={"a": child_a, "b": child_a}).__node_metadata
    assert meta.name == "switch"
    assert "_case_keys" in meta.properties
