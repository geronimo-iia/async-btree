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


def test_root_name(kernel):
    rooted = alias(child=a_func, name='a_func')
    assert rooted.__node_metadata.name == 'a_func'
    assert kernel.run(rooted) == 'a'


def test_decorate(kernel):
    async def b_decorator(child_value, other=''):
        return f'b{child_value}{other}'

    assert kernel.run(decorate(a_func, b_decorator)) == 'ba'

    assert kernel.run(decorate(a_func, b_decorator, other='c')) == 'bac'


def test_always_success(kernel):
    assert kernel.run(always_success(success_func)) == SUCCESS
    assert kernel.run(always_success(failure_func)) == SUCCESS
    assert kernel.run(always_success(exception_func)) == SUCCESS
    assert kernel.run(always_success(a_func)) == 'a'


def test_always_failure(kernel):
    assert kernel.run(always_failure(success_func)) == FAILURE
    assert kernel.run(always_failure(failure_func)) == FAILURE
    assert not kernel.run(always_failure(exception_func))
    assert isinstance(kernel.run(always_failure(exception_func)), ExceptionDecorator)
    assert kernel.run(always_failure(empty_func)) == []


def test_is_success(kernel):
    assert kernel.run(is_success(success_func))
    assert not kernel.run(is_success(failure_func))
    assert not kernel.run(is_success(exception_func))
    assert kernel.run(is_success(a_func))
    assert not kernel.run(is_success(empty_func))


def test_is_failure(kernel):
    assert not kernel.run(is_failure(success_func))
    assert kernel.run(is_failure(failure_func))
    assert kernel.run(is_failure(exception_func))
    assert not kernel.run(is_failure(a_func))
    assert kernel.run(is_failure(empty_func))


def test_inverter(kernel):
    assert not kernel.run(inverter(success_func))
    assert kernel.run(inverter(failure_func))
    with pytest.raises(RuntimeError):
        kernel.run(inverter(exception_func))
    assert not kernel.run(inverter(a_func))
    assert kernel.run(inverter(empty_func))


def test_retry(kernel):

    counter = ContextVar('counter_test_retry', default=5)

    async def tick():
        value = counter.get()
        counter.set(value - 1)
        if value <= 0:
            return SUCCESS
        if value == 3:
            raise RuntimeError('3')
        return FAILURE

    result = kernel.run(retry(tick))
    assert not result
    assert isinstance(result, ExceptionDecorator)
    assert kernel.run(retry(tick))

    counter.set(10)
    assert kernel.run(retry(tick, max_retry=11))

    counter.set(100)
    assert kernel.run(retry(tick, max_retry=-1))

    # negative
    with pytest.raises(AssertionError):
        retry(tick, max_retry=-2)


def test_retry_until_success(kernel):
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
    assert kernel.run(retry_until_success(tick))


def test_retry_until_failed(kernel):
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
    assert kernel.run(retry_until_failed(tick))
