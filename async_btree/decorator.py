"""
decorator module define all decorator function node.
"""
from typing import Awaitable
from .common import node_metadata, SUCCESS, FAILURE, ControlFlowException

__all__ = [
    "alias",
    "decorate",
    "always_success",
    "always_failure",
    "is_success",
    "is_failure",
    "inverter",
    "retry",
    "retry_until_success",
    "retry_until_failed"
]


def alias(child: Awaitable, name: str) -> Awaitable:
    """
    alias add a specifc name on our child.

    :param child: child function to decorate
    :param name: name of function tree
    :return: an Awaitable function.
    """

    @node_metadata(name=name)
    async def _alias():
        return await child()

    return _alias


def decorate(child: Awaitable, decorator: Awaitable, **kwargs) -> Awaitable:
    """
    Post process a child with specified decorator function.
    First argument of decorator function must be a child.

    This method implement a simple lazy evaluation.

    :param child: child function to decorate
    :param decorator: awaitable target decorator
    :return: an Awaitable function which return decorator evaluation against child.
    """

    @node_metadata(properties=["decorator"])
    async def _decorate():
        return await decorator(await child(), **kwargs)

    return _decorate


def always_success(child: Awaitable) -> Awaitable:
    """
    Always return SUCCESS value.

    :param child: child function to decorate
    :return: an Awaitable function which return child result if is truthy else SUCCESS (Any exception will be ignored). 

    """

    @node_metadata()
    async def _always_success():
        result = SUCCESS

        try:
            child_result = await child()
            if child_result:
                result = child_result

        except Exception:  # pylint: disable=broad-except
            pass

        return result

    return _always_success


def always_failure(child: Awaitable) -> Awaitable:  # -> Awaitable:
    """
    Always return FAILURE value.

    :param child: child function to decorate
    :return: an Awaitable function which return child result if is falsy else FAILURE,
        or a ControlFlowException if error occurs.

    """

    @node_metadata()
    async def _always_failure():
        result = FAILURE

        try:
            child_result = await child()
            if not child_result:
                result = child_result

        except Exception as e:  # pylint: disable=bare-except,broad-except
            result = ControlFlowException(e)

        return result

    return _always_failure


def is_success(child: Awaitable) -> Awaitable:
    """
    :param child: child function to decorate
    :return: an Awaitable function which return SUCCESS if child return SUCCESS else FAILURE.
        An exception will be evaluated as falsy.
    """

    @node_metadata()
    async def _is_success():
        try:
            return SUCCESS if bool(await child()) else FAILURE
        except Exception as e:  # pylint: disable=bare-except,broad-except
            return ControlFlowException(e)

    return _is_success


def is_failure(child: Awaitable) -> Awaitable:
    """
    :param child: child function to decorate
    :return:  an Awaitable function which return SUCCESS if child return FAILURE else FAILURE.
        An exception will be evaluated as a success.
    """

    @node_metadata()
    async def _is_failure():
        try:
            return SUCCESS if not bool(await child()) else FAILURE
        except: #pylint: disable=bare-except
            return SUCCESS

    return _is_failure


def inverter(child: Awaitable) -> Awaitable:
    """
    Invert node status.

    :param child: child function to decorate
    :return:  an Awaitable function which return SUCCESS if child return FAILURE else FAILURE
    """

    @node_metadata()
    async def _inverter():
        return not await child()

    return _inverter


def retry(child: Awaitable, max_retry: int = 3) -> Awaitable:
    """
    Retry child evaluation at most max_retry time on failure until child succeed.

    :param child: child function to decorate
    :param max_retry: max retry count (default 3), -1 mean infinite retry

    :return: an Awaitable function which retry child evaluation at most max_retry time on failure
        until child succeed.
        If max_retry is reached, returns FAILURE or last exception.
    """
    assert max_retry > 0 or max_retry == -1

    @node_metadata(properties=["max_retry"])
    async def _retry():
        retry_count = 0
        infinite_retry_condition = max_retry == -1
        result = FAILURE

        while infinite_retry_condition or retry_count < max_retry:
            try:
                result = await child()
                if result:
                    return result

            except Exception as e:  # pylint: disable=broad-except
                # return last failure exception
                if (
                    not infinite_retry_condition
                ):  # avoid data allocation if never returned
                    result = ControlFlowException(e)

            if not infinite_retry_condition:  # avoid overflow
                retry_count += 1

        return result

    return _retry


def retry_until_success(child: Awaitable) -> Awaitable:
    """
    Retry child until success.

    :param child: child function to decorate
    :return: an Awaitable function which try to evaluate child until it succeed.
    """

    # @node_metadata()
    # async def _retry_until_success():
    #    return await retry(child=child, max_retry=-1)()

    return node_metadata(name="retry_until_success")(retry(child=child, max_retry=-1))


def retry_until_failed(child: Awaitable) -> Awaitable:
    """
    Retry child until failed.

    :param child: child function to decorate
    :return: an Awaitable function which try to evaluate child until it failed.
    """

    # @node_metadata()
    # async def _retry_until_failed():
    #    return await retry(child=inverter(child=child), max_retry=-1)()

    return node_metadata(name="retry_until_failed")(
        retry(child=inverter(child), max_retry=-1)
    )
