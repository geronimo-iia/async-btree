"""Leaf definition."""

from .decorator import is_success
from .definition import (
    AsyncInnerFunction,
    CallableFunction,
    ControlFlowException,
    alias_node_metadata,
    node_metadata,
)
from .utils import to_async

__all__ = ["action", "condition"]


def action(target: CallableFunction, **kwargs) -> AsyncInnerFunction:
    """Declare an action leaf.

    Action is an awaitable closure of specified function,
    (See alias function).

    Args:
        target (CallableFunction): awaitable function
        kwargs: optional kwargs argument to pass on target function

    Returns:
        (AsyncInnerFunction): an awaitable function.

    Raises:
        ControlFlowException : if error occurs

    """

    _target = to_async(target)

    @node_metadata(properties=["_target"])
    async def _action():
        try:
            return await _target(**kwargs)
        except Exception as e:
            raise ControlFlowException.instanciate(e)

    return _action


def condition(target: CallableFunction, **kwargs) -> AsyncInnerFunction:
    """Declare a condition leaf.

    Condition is an awaitable closure of specified function.

    Args:
        target (CallableFunction):  awaitable function which be evaluated as True/False.
        kwargs: optional kwargs argument to pass on target function

    Returns:
        (AsyncInnerFunction): an awaitable function.
    """
    return alias_node_metadata(
        name="condition",
        target=is_success(action(target=target, **kwargs)),
        properties=["target"],
    )
