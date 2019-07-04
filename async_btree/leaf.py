"""Leaf definition."""

from .decorator import is_success
from .definition import (
    AsyncInnerFunction,
    CallableFunction,
    ExceptionDecorator,
    node_metadata,
)


__all__ = ['action', 'condition']


def action(target: CallableFunction, **kwargs) -> AsyncInnerFunction:
    """Declare an action leaf.

    Action is an awaitable closure of specified function.
    :param target: awaitable function
    :param kwargs: optional kwargs argument to pass on target function
    :return: an awaitable function.
    """

    @node_metadata(properties=['target'])
    async def _action():
        try:
            return await target(**kwargs)
        except Exception as e:
            return ExceptionDecorator(exception=e)

    return _action


def condition(target: CallableFunction, **kwargs) -> AsyncInnerFunction:
    """Declare a condition leaf.

    Condition is an awaitable closure of specified function.
    :param target: awaitable function which be evaluated as True/False.
    :param kwargs: optional kwargs argument to pass on target function
    :return: an awaitable function.
    """

    # @node_metadata(properties=["target"])
    # async def _condition():
    #    return is_success(child=action(target=target, *args, **kwargs))()

    return node_metadata(name='condition', properties=['target'])(
        is_success(action(target=target, **kwargs))
    )
