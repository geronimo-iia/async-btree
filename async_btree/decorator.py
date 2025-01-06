"""Decorator module define all decorator function node."""

from typing import Any

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
    "decorate",
    "ignore_exception",
    "always_success",
    "always_failure",
    "is_success",
    "is_failure",
    "inverter",
    "retry",
    "retry_until_success",
    "retry_until_failed",
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
    """Create a decorator.

    Post process a child with specified decorator function.
    First argument of decorator function must be a child.

    This method implement a simple lazy evaluation.

    Args:
        child (CallableFunction): child function to decorate
        decorator (CallableFunction): awaitable target decorator with profile 'decorator(child_result, **kwargs)'
        kwargs: optional keyed argument to pass to decorator function

    Returns:
      (AsyncInnerFunction): an awaitable function which
            return decorator evaluation against child.
    """

    _child = to_async(child)
    _decorator = to_async(decorator)

    @node_metadata(properties=["_decorator"])
    async def _decorate():
        return await _decorator(await _child(), **kwargs)

    return _decorate


def ignore_exception(child: CallableFunction) -> AsyncInnerFunction:
    """Create a node which ignore runtime exception.

    Args:
        child (CallableFunction): child function to decorate

    Returns:
        (AsyncInnerFunction): an awaitable function which return child result
        or any exception with a falsy meaning in a ControlFlowException.

    """

    _child = to_async(child)

    @node_metadata()
    async def _ignore_exception():
        try:
            return await _child()

        except Exception as e:
            return ControlFlowException.instanciate(e)

    return _ignore_exception


def always_success(child: CallableFunction) -> AsyncInnerFunction:
    """Create a node which always return SUCCESS value.

    Note:
        If you wanna git a success even if an exception occurs, you have
        to decorate child with ignore_exception, like this:

        `always_success(child=ignore_exception(myfunction))`


    Args:
        child (CallableFunction): child function to decorate

    Returns:
        (AsyncInnerFunction): an awaitable function which return child result if it is truthy
            else SUCCESS.

    Raises:
        ControlFlowException : if error occurs

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
            raise ControlFlowException.instanciate(e)

        return result

    return _always_success


def always_failure(child: CallableFunction) -> AsyncInnerFunction:  # -> Awaitable:
    """Produce a function which always return FAILURE value.

    Note:
        If you wanna git a failure even if an exception occurs, you have
        to decorate child with ignore_exception, like this:

        `always_failure(child=ignore_exception(myfunction))`

    Args:
        child (CallableFunction): child function to decorate

    Returns:
        (AsyncInnerFunction): an awaitable function which return child result if is falsy
            else FAILURE.

    Raises:
        ControlFlowException : if error occurs

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
            raise ControlFlowException.instanciate(e)

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
    """Create a conditional node which test if child fail.

    Args:
        child (CallableFunction): child function to decorate

    Returns:
        (AsyncInnerFunction): an awaitable function which return SUCCESS if child
            return FAILURE else FAILURE.
    """

    _child = to_async(child)

    @node_metadata()
    async def _is_failure():
        return SUCCESS if not bool(await _child()) else FAILURE

    return _is_failure


def inverter(child: CallableFunction) -> AsyncInnerFunction:
    """Invert node status.

    Args:
        child (CallableFunction): child function to decorate

    Returns:
        (AsyncInnerFunction): an awaitable function which return SUCCESS if child
            return FAILURE else SUCCESS
    """

    _child = to_async(child)

    @node_metadata()
    async def _inverter():
        return not bool(await _child())

    return _inverter


def retry(child: CallableFunction, max_retry: int = 3) -> AsyncInnerFunction:
    """Retry child evaluation at most max_retry time on failure until child succeed.

    Args:
        child (CallableFunction): child function to decorate
        max_retry (int): max retry count (default 3), -1 mean infinite retry

    Returns:
        (AsyncInnerFunction): an awaitable function which retry child evaluation
            at most max_retry time on failure until child succeed.
            If max_retry is reached, returns FAILURE or last exception.
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
            print(f"result : {result}")
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
