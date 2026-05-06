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
    """Declare an action leaf node.

    Wraps `target` as an awaitable closure. Any exception raised by `target`
    is caught and re-raised as a `ControlFlowException`, giving it falsy meaning.

    Args:
        target (CallableFunction): sync or async callable to invoke.
        kwargs: keyword arguments forwarded to `target` on each call.

    Returns:
        (AsyncInnerFunction): an awaitable function.

    Raises:
        ControlFlowException: wrapping any exception raised by `target`.
    """

    _target = to_async(target)

    @node_metadata(properties=["_target"])
    async def _action():
        try:
            return await _target(**kwargs)
        except Exception as e:
            raise ControlFlowException.instantiate(e) from e

    return _action


def condition(target: CallableFunction, **kwargs) -> AsyncInnerFunction:
    """Declare a condition leaf node.

    Delegates to `is_success(action(target, **kwargs))` — returns `SUCCESS` if `target`
    is truthy, `FAILURE` otherwise. Exceptions from `target` propagate as
    `ControlFlowException`.

    Args:
        target (CallableFunction): sync or async callable evaluated as a boolean.
        kwargs: keyword arguments forwarded to `target` on each call.

    Returns:
        (AsyncInnerFunction): an awaitable function that returns `SUCCESS` or `FAILURE`.
    """
    return alias_node_metadata(
        name="condition",
        target=is_success(action(target=target, **kwargs)),
        properties=["target"],
    )
