"""
Leaf definition.
"""
from typing import Awaitable
from .common import node_metadata, ControlFlowException
from .decorator import is_success

__all__ = ["action", "condition"]


def action(target: Awaitable, **kwargs) -> Awaitable:
    """
    Action is an awaitable closure of specified function
    :param target: awaitable function
    :param kwargs: optional kwargs argument to pass on target function
    :return: an awaitable function.
    """

    @node_metadata(properties=["target"])
    async def _action():
        try:
            return await target(**kwargs)
        except Exception as e:  # pylint: disable=broad-except
            return ControlFlowException(exception=e)

    return _action


def condition(target: Awaitable, **kwargs) -> Awaitable:
    """
    Condition is an awaitable closure of specified function.
    :param target: awaitable function which be evaluated as True/False.
    :param kwargs: optional kwargs argument to pass on target function
    :return: an awaitable function.
    """

    # @node_metadata(properties=["target"])
    # async def _condition():
    #    return is_success(child=action(target=target, *args, **kwargs))()

    return node_metadata(name="condition", properties=["target"])(
        is_success(action(target=target, **kwargs))
    )
