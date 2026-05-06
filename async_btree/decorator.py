"""Decorator module define all decorator function node."""

import time
from typing import Any

import anyio

from .definition import (
    FAILURE,
    SUCCESS,
    AsyncInnerFunction,
    CallableFunction,
    ControlFlowException,
    alias_node_metadata,
    node_metadata,
)
from .utils import to_async

__all__ = [
    "alias",
    "always_failure",
    "always_success",
    "cooldown",
    "decorate",
    "delay",
    "ignore_exception",
    "inverter",
    "is_failure",
    "is_success",
    "retry",
    "retry_until_failed",
    "retry_until_success",
    "timeout_after",
]


def alias(child: CallableFunction, name: str) -> AsyncInnerFunction:
    """Define an alias on our child.

    Args:
        child (CallableFunction): child function to decorate
        name (str): name of function tree

    Returns:
        (AsyncInnerFunction): an awaitable function.
    """

    _child = to_async(child)

    # we use a dedicted function to 'duplicate' the child reference
    @node_metadata(name=name)
    async def _alias():
        return await _child()

    return _alias


def decorate(child: CallableFunction, decorator: CallableFunction, **kwargs) -> AsyncInnerFunction:
    """Post-process child result with a decorator function.

    Runs child eagerly, then passes the result as the first argument to `decorator`.

    Args:
        child (CallableFunction): sync or async callable to run first.
        decorator (CallableFunction): sync or async callable with signature
            `decorator(child_result, **kwargs)`.
        kwargs: additional keyword arguments forwarded to `decorator`.

    Returns:
        (AsyncInnerFunction): an awaitable function that returns `decorator(child_result, **kwargs)`.
    """

    _child = to_async(child)
    _decorator = to_async(decorator)

    @node_metadata(properties=["_decorator"])
    async def _decorate():
        return await _decorator(await _child(), **kwargs)

    return _decorate


def ignore_exception(child: CallableFunction) -> AsyncInnerFunction:
    """Wrap child so exceptions are caught and returned as a falsy value instead of propagating.

    Args:
        child (CallableFunction): sync or async callable to wrap.

    Returns:
        (AsyncInnerFunction): an awaitable function that returns child result unchanged on
            success, or a `ControlFlowException` wrapping the exception on failure.
            The returned exception is falsy.
    """

    _child = to_async(child)

    @node_metadata()
    async def _ignore_exception():
        try:
            return await _child()

        except Exception as e:
            return ControlFlowException.instantiate(e)

    return _ignore_exception


def always_success(child: CallableFunction) -> AsyncInnerFunction:
    """Wrap child so the node always returns a truthy value.

    If child returns a truthy result, that original result is preserved and returned.
    If child returns a falsy result, returns `SUCCESS` instead.
    Exceptions are re-raised as `ControlFlowException`.

    Note:
        To suppress exceptions as well, wrap child with `ignore_exception` first:

        `always_success(child=ignore_exception(myfunction))`

    Args:
        child (CallableFunction): sync or async callable to wrap.

    Returns:
        (AsyncInnerFunction): an awaitable function that returns the original truthy child
            result unchanged, or `SUCCESS` if child is falsy.

    Raises:
        ControlFlowException: if child raises an exception.
    """

    _child = to_async(child)

    @node_metadata()
    async def _always_success():
        result: Any = SUCCESS

        try:
            child_result = await _child()
            if bool(child_result):
                result = child_result

        except Exception as e:
            raise ControlFlowException.instantiate(e) from e

        return result

    return _always_success


def always_failure(child: CallableFunction) -> AsyncInnerFunction:
    """Wrap child so the node always returns a falsy value.

    If child returns a falsy result, that original result is preserved and returned.
    If child returns a truthy result, returns `FAILURE` instead.
    Exceptions are re-raised as `ControlFlowException`.

    Note:
        To suppress exceptions as well, wrap child with `ignore_exception` first:

        `always_failure(child=ignore_exception(myfunction))`

    Args:
        child (CallableFunction): sync or async callable to wrap.

    Returns:
        (AsyncInnerFunction): an awaitable function that returns the original falsy child
            result unchanged, or `FAILURE` if child is truthy.

    Raises:
        ControlFlowException: if child raises an exception.
    """

    _child = to_async(child)

    @node_metadata()
    async def _always_failure():
        result: Any = FAILURE

        try:
            child_result = await _child()
            if not bool(child_result):
                result = child_result

        except Exception as e:
            raise ControlFlowException.instantiate(e) from e

        return result

    return _always_failure


def is_success(child: CallableFunction) -> AsyncInnerFunction:
    """Create a conditional node which test if child success.

    Args:
        child (CallableFunction): child function to decorate

    Returns:
        (AsyncInnerFunction): an awaitable function which return SUCCESS if child
            return SUCCESS else FAILURE.
    """

    _child = to_async(child)

    @node_metadata()
    async def _is_success():
        return SUCCESS if bool(await _child()) else FAILURE

    return _is_success


def is_failure(child: CallableFunction) -> AsyncInnerFunction:
    """Return `SUCCESS` if child is falsy, `FAILURE` otherwise.

    Args:
        child (CallableFunction): sync or async callable to test.

    Returns:
        (AsyncInnerFunction): an awaitable function that returns `SUCCESS` if child
            result is falsy, `FAILURE` if child result is truthy.
    """

    _child = to_async(child)

    @node_metadata()
    async def _is_failure():
        return SUCCESS if not bool(await _child()) else FAILURE

    return _is_failure


def inverter(child: CallableFunction) -> AsyncInnerFunction:
    """Invert node status.

    Args:
        child (CallableFunction): sync or async callable to invert.

    Returns:
        (AsyncInnerFunction): an awaitable function that returns `SUCCESS` if child
            is falsy, else `FAILURE`.
    """

    _child = to_async(child)

    @node_metadata()
    async def _inverter():
        return not bool(await _child())

    return _inverter


def retry(child: CallableFunction, max_retry: int = 3) -> AsyncInnerFunction:
    """Retry child evaluation on failure until it succeeds or `max_retry` attempts are exhausted.

    Args:
        child (CallableFunction): sync or async callable to retry.
        max_retry (int): maximum number of attempts (default 3). Use `-1` for infinite retries.

    Returns:
        (AsyncInnerFunction): an awaitable function that returns the first truthy result, or
            the last falsy result (which may be a `ControlFlowException`) if all attempts fail.

    Raises:
        AssertionError: if `max_retry` is 0 or negative (other than -1).
    """
    if not (max_retry > 0 or max_retry == -1):
        raise AssertionError("max_retry")

    _child = to_async(child)

    @node_metadata(properties=["max_retry"])
    async def _retry():
        retry_count = max_retry
        result: Any = FAILURE

        while not bool(result) and retry_count != 0:
            result = await _child()
            retry_count -= 1

        return result

    return _retry


def retry_until_success(child: CallableFunction) -> AsyncInnerFunction:
    """Retry child until success.

    Args:
        child (CallableFunction): child function to decorate

    Returns:
        (AsyncInnerFunction): an awaitable function which try to evaluate child
            until it succeed.
    """
    return alias_node_metadata(name="retry_until_success", target=retry(child=child, max_retry=-1))


def retry_until_failed(child: CallableFunction) -> AsyncInnerFunction:
    """Retry child until failed.

    Args:
        child (CallableFunction): child function to decorate

    Returns:
        (AsyncInnerFunction): an awaitable function which try to evaluate child
            until it failed.
    """

    return alias_node_metadata(name="retry_until_failed", target=retry(child=inverter(child), max_retry=-1))


def timeout_after(child: CallableFunction, delay: float) -> AsyncInnerFunction:
    """Run child with a time limit; return `FAILURE` if the deadline is exceeded.

    Args:
        child (CallableFunction): sync or async callable to run.
        delay (float): maximum seconds to wait before returning `FAILURE`.

    Returns:
        (AsyncInnerFunction): an awaitable function that returns child result on
            success, or `FAILURE` if the deadline is exceeded.
    """
    _child = to_async(child)

    @node_metadata(properties=["delay"])
    async def _timeout_after():
        result: Any = FAILURE
        with anyio.move_on_after(delay) as cancel_scope:
            result = await _child()
        if cancel_scope.cancelled_caught:
            return FAILURE
        return result

    return _timeout_after


def cooldown(child: CallableFunction, delay: float, throttled_value: Any = SUCCESS) -> AsyncInnerFunction:
    """Skip child if called again before `delay` seconds have elapsed since the last run.

    Last-run time is stored in the closure — it persists across `BTreeRunner.run()` ticks
    for the lifetime of this node instance.

    Args:
        child (CallableFunction): sync or async callable to throttle.
        delay (float): minimum seconds between successive executions of child.
        throttled_value (Any): value returned when child is skipped. Defaults to `SUCCESS`.

    Returns:
        (AsyncInnerFunction): an awaitable function that runs child and returns its result
            when the cooldown has elapsed, or `throttled_value` when the call is throttled.
    """
    _child = to_async(child)
    _last_run: list[float] = [0.0]  # list to allow mutation from inner scope

    @node_metadata(properties=["delay"])
    async def _cooldown() -> Any:
        now = time.monotonic()
        if now - _last_run[0] < delay:
            return throttled_value
        _last_run[0] = now
        return await _child()

    return _cooldown


def delay(child: CallableFunction, seconds: float) -> AsyncInnerFunction:
    """Wait `seconds` before running child.

    Args:
        child (CallableFunction): sync or async callable to run after the delay.
        seconds (float): number of seconds to wait before executing child.

    Returns:
        (AsyncInnerFunction): an awaitable function that sleeps then returns child result.
    """
    _child = to_async(child)

    @node_metadata(properties=["seconds"])
    async def _delay():
        await anyio.sleep(seconds)
        return await _child()

    return _delay
