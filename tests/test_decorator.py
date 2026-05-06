from contextvars import ContextVar

import anyio
import pytest

from async_btree import (
    FAILURE,
    SUCCESS,
    ControlFlowException,
    alias,
    always_failure,
    always_success,
    cooldown,
    decorate,
    delay,
    ignore_exception,
    inverter,
    is_failure,
    is_success,
    retry,
    retry_until_failed,
    retry_until_success,
    timeout_after,
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


async def failure_func():
    return FAILURE


async def success_func():
    return SUCCESS


async def exception_func():
    raise RuntimeError()


async def empty_func():
    return []


async def test_alias_name():
    rooted = alias(child=a_func, name="a_func")
    assert rooted.__node_metadata.name == "a_func"
    assert await rooted() == "a"


async def test_alias_not_override():
    a_rooted = alias(child=a_func, name="a_func")
    b_rooted = alias(child=a_func, name="b_func")
    assert a_rooted.__node_metadata.name == "a_func"
    assert b_rooted.__node_metadata.name == "b_func"


async def test_decorate():
    async def b_decorator(child_value, other=""):
        return f"b{child_value}{other}"

    assert await decorate(a_func, b_decorator)() == "ba"

    assert await decorate(a_func, b_decorator, other="c")() == "bac"
    meta = decorate(a_func, b_decorator).__node_metadata
    assert meta.name == "decorate"
    assert "_decorator" in meta.properties


async def test_always_success():
    assert await always_success(success_func)() == SUCCESS
    assert await always_success(failure_func)() == SUCCESS
    with pytest.raises(ControlFlowException):
        await always_success(exception_func)()
    assert await always_success(a_func)() == "a"

    meta = always_success(a_func).__node_metadata
    assert meta.name == "always_success"


async def test_always_failure():
    assert await always_failure(success_func)() == FAILURE
    assert await always_failure(failure_func)() == FAILURE
    with pytest.raises(ControlFlowException):
        await always_failure(exception_func)()
    assert isinstance(await always_failure(ignore_exception(exception_func))(), ControlFlowException)
    assert await always_failure(empty_func)() == []

    meta = always_failure(empty_func).__node_metadata
    assert meta.name == "always_failure"


async def test_is_success():
    assert await is_success(success_func)()
    assert not await is_success(failure_func)()
    with pytest.raises(RuntimeError):
        await is_success(exception_func)()
    assert await is_success(a_func)()
    assert not await is_success(empty_func)()


async def test_is_failure():
    assert not await is_failure(success_func)()
    assert await is_failure(failure_func)()
    with pytest.raises(RuntimeError):
        assert await is_failure(exception_func)()
    assert not await is_failure(a_func)()
    assert await is_failure(empty_func)()

    meta = is_failure(empty_func).__node_metadata
    assert meta.name == "is_failure"


async def test_inverter():
    assert not await inverter(success_func)()
    assert await inverter(failure_func)()
    with pytest.raises(RuntimeError):
        await inverter(exception_func)()
    assert not await inverter(a_func)()
    assert await inverter(empty_func)()

    meta = inverter(a_func).__node_metadata
    assert meta.name == "inverter"


async def test_retry():
    counter = ContextVar("counter_test_retry", default=5)

    async def tick():
        value = counter.get()
        counter.set(value - 1)
        print(f"value: {value}")
        if value <= 0:
            return SUCCESS
        if value == 3:
            raise RuntimeError("3")
        return FAILURE

    result = await retry(ignore_exception(tick))()  # counter: 5, 4, 3
    assert not result
    assert isinstance(result, ControlFlowException)

    assert await retry(tick)()  # counter: 2, 1, 0

    # let raise RuntimeError
    counter.set(3)
    with pytest.raises(RuntimeError):
        await tick()

    counter.set(10)
    assert await retry(ignore_exception(tick), max_retry=11)()

    counter.set(100)
    assert await retry(ignore_exception(tick), max_retry=-1)()

    with pytest.raises(AssertionError):
        retry(ignore_exception(tick), max_retry=0)
    with pytest.raises(AssertionError):
        retry(ignore_exception(tick), max_retry=-2)

    meta = retry(ignore_exception(tick)).__node_metadata
    assert meta.name == "retry"
    assert "max_retry" in meta.properties


async def test_retry_until_success():
    counter = ContextVar("counter_test_retry_until_success", default=5)

    async def tick():
        value = counter.get()
        counter.set(value - 1)
        if value <= 0:
            return SUCCESS
        if value == 3:
            raise RuntimeError("3")
        return FAILURE

    counter.set(100)
    assert await retry_until_success(ignore_exception(tick))()

    meta = retry_until_success(ignore_exception(tick)).__node_metadata
    assert meta.name == "retry_until_success"
    assert "max_retry" in meta.properties


async def test_retry_until_failed():
    counter = ContextVar("counter_test_retry_until_failed", default=5)

    async def tick():
        value = counter.get()
        counter.set(value - 1)
        if value <= 0:
            return SUCCESS
        if value == 3:
            raise RuntimeError("3")
        return FAILURE

    counter.set(100)
    assert await retry_until_failed(tick)()

    meta = retry_until_failed(ignore_exception(tick)).__node_metadata
    assert meta.name == "retry_until_failed"
    assert "max_retry" in meta.properties


async def test_timeout_after_completes_in_time():
    async def fast():
        return SUCCESS

    result = await timeout_after(child=fast, delay=5.0)()
    assert result is SUCCESS


async def test_timeout_after_exceeds_deadline():
    async def slow():
        await anyio.sleep(10.0)
        return SUCCESS

    result = await timeout_after(child=slow, delay=0.01)()
    assert result is FAILURE


async def test_timeout_after_returns_child_value():
    async def child():
        return "hello"

    result = await timeout_after(child=child, delay=5.0)()
    assert result == "hello"


async def test_timeout_after_metadata():
    async def fast():
        return SUCCESS

    meta = timeout_after(child=fast, delay=1.0).__node_metadata
    assert meta.name == "timeout_after"
    assert "delay" in meta.properties


async def test_cooldown_runs_first_call():
    async def child():
        return "ran"

    result = await cooldown(child=child, delay=10.0)()
    assert result == "ran"


async def test_cooldown_throttles_second_call():
    async def child():
        return "ran"

    node = cooldown(child=child, delay=10.0)
    await node()
    result = await node()
    assert result is SUCCESS  # default throttled_value


async def test_cooldown_custom_throttled_value():
    async def child():
        return "ran"

    node = cooldown(child=child, delay=10.0, throttled_value=FAILURE)
    await node()
    result = await node()
    assert result is FAILURE


async def test_cooldown_runs_after_delay():
    async def child():
        return "ran"

    node = cooldown(child=child, delay=0.01)
    await node()
    await anyio.sleep(0.02)
    result = await node()
    assert result == "ran"


async def test_cooldown_metadata():
    async def child():
        return SUCCESS

    meta = cooldown(child=child, delay=1.0).__node_metadata
    assert meta.name == "cooldown"
    assert "delay" in meta.properties


async def test_delay_runs_child():
    async def child():
        return "done"

    result = await delay(child=child, seconds=0.01)()
    assert result == "done"


async def test_delay_waits_before_running():
    import time

    start = time.monotonic()
    await delay(child=lambda: SUCCESS, seconds=0.05)()
    elapsed = time.monotonic() - start
    assert elapsed >= 0.04


async def test_delay_metadata():
    async def child():
        return SUCCESS

    meta = delay(child=child, seconds=1.0).__node_metadata
    assert meta.name == "delay"
    assert "seconds" in meta.properties
