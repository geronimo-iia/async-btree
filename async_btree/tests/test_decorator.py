from libellule.control_flow.common import SUCCESS, FAILURE, ControlFlowException
from libellule.control_flow.decorator import *
from curio import run
from contextvars import ContextVar

import pytest


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


counter = ContextVar("counter", default=5)


async def tick():
    value = counter.get()
    counter.set(value - 1)
    if value <= 0:
        return SUCCESS
    if value == 3:
        raise RuntimeError("3")
    return FAILURE


def test_root_name():
    rooted = alias(a_func, name="a_func")
    assert rooted.__node_metadata.name == "a_func"
    assert run(rooted) == "a"

def test_decorate():
    async def b_decorator(child_value, other=""):
        return f"b{child_value}{other}"

    assert run(decorate(a_func, b_decorator)) == "ba"

    assert run(decorate(a_func, b_decorator, other="c")) == "bac"


def test_always_success():
    assert run(always_success(success_func)) == SUCCESS
    assert run(always_success(failure_func)) == SUCCESS
    assert run(always_success(exception_func)) == SUCCESS
    assert run(always_success(a_func)) == "a"


def test_always_failure():
    assert run(always_failure(success_func)) == FAILURE
    assert run(always_failure(failure_func)) == FAILURE
    assert not run(always_failure(exception_func))
    assert isinstance(run(always_failure(exception_func)), ControlFlowException)
    assert run(always_failure(empty_func)) == []


def test_is_success():
    assert run(is_success(success_func))
    assert not run(is_success(failure_func))
    assert not run(is_success(exception_func))
    assert run(is_success(a_func))
    assert not run(is_success(empty_func))


def test_is_failure():
    assert not run(is_failure(success_func))
    assert run(is_failure(failure_func))
    assert run(is_failure(exception_func))
    assert not run(is_failure(a_func))
    assert run(is_failure(empty_func))


def test_inverter():
    assert not run(inverter(success_func))
    assert run(inverter(failure_func))
    with pytest.raises(RuntimeError):
        run(inverter(exception_func))
    assert not run(inverter(a_func))
    assert run(inverter(empty_func))


def test_retry():

    result = run(retry(tick))
    assert not result
    assert isinstance(result, ControlFlowException)
    assert run(retry(tick))

    counter.set(10)
    assert run(retry(tick, max_retry=11))

    counter.set(100)
    assert run(retry(tick, max_retry=-1))


def test_retry_until_success():
    counter.set(100)
    assert run(retry_until_success(tick))


def test_retry_until_failed():
    counter.set(100)
    assert run(retry_until_failed(tick))
