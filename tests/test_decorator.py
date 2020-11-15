from contextvars import ContextVar

import pytest

from async_btree import (
    FAILURE,
    SUCCESS,
    ExceptionDecorator,
    alias,
    always_failure,
    always_success,
    decorate,
    inverter,
    is_failure,
    is_success,
    retry,
    retry_until_failed,
    retry_until_success,
)


async def a_func():
    return 'a'


async def failure_func():
    return FAILURE


async def success_func():
    return SUCCESS


async def exception_func():
    raise RuntimeError()


async def empty_func():
    return []


@pytest.mark.curio
async def test_root_name(kernel):
    rooted = alias(child=a_func, name='a_func')
    assert rooted.__node_metadata.name == 'a_func'
    assert await rooted() == 'a'


@pytest.mark.curio
async def test_decorate(kernel):
    async def b_decorator(child_value, other=''):
        return f'b{child_value}{other}'

    assert await decorate(a_func, b_decorator)() == 'ba'

    assert await decorate(a_func, b_decorator, other='c')() == 'bac'


@pytest.mark.curio
async def test_always_success(kernel):
    assert await always_success(success_func)() == SUCCESS
    assert await always_success(failure_func)() == SUCCESS
    assert await always_success(exception_func)() == SUCCESS
    assert await always_success(a_func)() == 'a'


@pytest.mark.curio
async def test_always_failure(kernel):
    assert await always_failure(success_func)() == FAILURE
    assert await always_failure(failure_func)() == FAILURE
    assert not await always_failure(exception_func)()
    assert isinstance(await always_failure(exception_func)(), ExceptionDecorator)
    assert await always_failure(empty_func)() == []


@pytest.mark.curio
async def test_is_success(kernel):
    assert await is_success(success_func)()
    assert not await is_success(failure_func)()
    assert not await is_success(exception_func)()
    assert await is_success(a_func)()
    assert not await is_success(empty_func)()


@pytest.mark.curio
async def test_is_failure(kernel):
    assert not await is_failure(success_func)()
    assert await is_failure(failure_func)()
    assert await is_failure(exception_func)()
    assert not await is_failure(a_func)()
    assert await is_failure(empty_func)()


@pytest.mark.curio
async def test_inverter(kernel):
    assert not await inverter(success_func)()
    assert await inverter(failure_func)()
    with pytest.raises(RuntimeError):
        await inverter(exception_func)()
    assert not await inverter(a_func)()
    assert await inverter(empty_func)()


@pytest.mark.curio
async def test_retry(kernel):

    counter = ContextVar('counter_test_retry', default=5)

    async def tick():
        value = counter.get()
        counter.set(value - 1)
        if value <= 0:
            return SUCCESS
        if value == 3:
            raise RuntimeError('3')
        return FAILURE

    result = await retry(tick)()
    assert not result
    assert isinstance(result, ExceptionDecorator)
    assert await retry(tick)()

    counter.set(10)
    assert await retry(tick, max_retry=11)()

    counter.set(100)
    assert await retry(tick, max_retry=-1)()

    # negative
    with pytest.raises(AssertionError):
        retry(tick, max_retry=-2)


@pytest.mark.curio
async def test_retry_until_success(kernel):
    counter = ContextVar('counter_test_retry_until_success', default=5)

    async def tick():
        value = counter.get()
        counter.set(value - 1)
        if value <= 0:
            return SUCCESS
        if value == 3:
            raise RuntimeError('3')
        return FAILURE

    counter.set(100)
    assert await retry_until_success(tick)()


@pytest.mark.curio
async def test_retry_until_failed(kernel):
    counter = ContextVar('counter_test_retry_until_failed', default=5)

    async def tick():
        value = counter.get()
        counter.set(value - 1)
        if value <= 0:
            return SUCCESS
        if value == 3:
            raise RuntimeError('3')
        return FAILURE

    counter.set(100)
    assert await retry_until_failed(tick)()
