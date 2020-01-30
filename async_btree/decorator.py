"""Decorator module define all decorator function node."""
from typing import Any

from .definition import FAILURE, SUCCESS, AsyncInnerFunction, CallableFunction, ExceptionDecorator, node_metadata

__all__ = [
    'alias',
    'decorate',
    'always_success',
    'always_failure',
    'is_success',
    'is_failure',
    'inverter',
    'retry',
    'retry_until_success',
    'retry_until_failed',
]


def alias(child: CallableFunction, name: str) -> AsyncInnerFunction:
    """Define an alias on our child.

    Args:
        child (CallableFunction): child function to decorate
        name (str): name of function tree

    Returns:
        (AsyncInnerFunction): an awaitable function.
    """

    @node_metadata(name=name)
    async def _alias():
        return await child()

    return _alias


def decorate(child: CallableFunction, decorator: CallableFunction, **kwargs) -> AsyncInnerFunction:
    """Create a decorator.

    Post process a child with specified decorator function.
    First argument of decorator function must be a child.

    This method implement a simple lazy evaluation.

    Args:
        child (CallableFunction): child function to decorate
        decorator (CallableFunction): awaitable target decorator
        kwargs: optional keyed argument to pass to decorator function

    Returns:
      (AsyncInnerFunction): an awaitable function which
            return decorator evaluation against child.
    """

    @node_metadata(properties=['decorator'])
    async def _decorate():
        return await decorator(await child(), **kwargs)

    return _decorate


def always_success(child: CallableFunction) -> AsyncInnerFunction:
    """Create a node which always return SUCCESS value.

    Args:
        child (CallableFunction): child function to decorate

    Returns:
        (AsyncInnerFunction): an awaitable function which return child result if is truthy
            else SUCCESS (Any exception will be ignored).

    """

    @node_metadata()
    async def _always_success():
        result: Any = SUCCESS

        try:
            child_result = await child()
            if child_result:
                result = child_result

        except Exception:
            return result

        return result

    return _always_success


def always_failure(child: CallableFunction) -> AsyncInnerFunction:  # -> Awaitable:
    """Produce a function which always return FAILURE value.

    Args:
        child (CallableFunction): child function to decorate

    Returns:
        (AsyncInnerFunction): an awaitable function which return child result if is falsy
            else FAILURE, or a ControlFlowException if error occurs.

    """

    @node_metadata()
    async def _always_failure():
        result: Any = FAILURE

        try:
            child_result = await child()
            if not child_result:
                result = child_result

        except Exception as e:
            result = ExceptionDecorator(e)

        return result

    return _always_failure


def is_success(child: CallableFunction) -> AsyncInnerFunction:
    """Create a conditional node which test if child success.

    Args:
        child (CallableFunction): child function to decorate

    Returns:
        (AsyncInnerFunction): an awaitable function which return SUCCESS if child
            return SUCCESS else FAILURE.
            An exception will be evaluated as falsy.
    """

    @node_metadata()
    async def _is_success():
        try:
            return SUCCESS if bool(await child()) else FAILURE
        except Exception as e:
            return ExceptionDecorator(e)

    return _is_success


def is_failure(child: CallableFunction) -> AsyncInnerFunction:
    """Create a conditional node which test if child fail.

    Args:
        child (CallableFunction): child function to decorate

    Returns:
        (AsyncInnerFunction): an awaitable function which return SUCCESS if child
            return FAILURE else FAILURE.
            An exception will be evaluated as a success.
    """

    @node_metadata()
    async def _is_failure():
        try:
            return SUCCESS if not bool(await child()) else FAILURE
        except Exception:  # pylint: disable=broad-except
            return SUCCESS

    return _is_failure


def inverter(child: CallableFunction) -> AsyncInnerFunction:
    """Invert node status.

    Args:
        child (CallableFunction): child function to decorate

    Returns:
        (AsyncInnerFunction): an awaitable function which return SUCCESS if child
            return FAILURE else SUCCESS
    """

    @node_metadata()
    async def _inverter():
        return not await child()

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
        raise AssertionError('max_retry')

    @node_metadata(properties=['max_retry'])
    async def _retry():
        retry_count = 0
        infinite_retry_condition = max_retry == -1
        result: Any = FAILURE

        while not result and (infinite_retry_condition or retry_count < max_retry):
            try:
                result = await child()

            except Exception as e:
                # return last failure exception
                if not infinite_retry_condition:  # avoid data allocation if never returned
                    result = ExceptionDecorator(e)

            retry_count += 1

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

    # @node_metadata()
    # async def _retry_until_success():
    #    return await retry(child=child, max_retry=-1)()

    return node_metadata(name='retry_until_success')(retry(child=child, max_retry=-1))


def retry_until_failed(child: CallableFunction) -> AsyncInnerFunction:
    """Retry child until failed.

    Args:
        child (CallableFunction): child function to decorate

    Returns:
        (AsyncInnerFunction): an awaitable function which try to evaluate child
            until it failed.
    """

    return node_metadata(name='retry_until_failed')(retry(child=inverter(child), max_retry=-1))
