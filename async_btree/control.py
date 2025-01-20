"""Control function definition."""

from typing import Any, Optional

from .definition import (
    FAILURE,
    SUCCESS,
    AsyncInnerFunction,
    CallableFunction,
    alias_node_metadata,
    node_metadata,
)
from .utils import to_async

__all__ = ["sequence", "fallback", "selector", "decision", "repeat_until"]


def sequence(children: list[CallableFunction], succes_threshold: Optional[int] = None) -> AsyncInnerFunction:
    """Return a function which execute children in sequence.

    succes_threshold parameter generalize traditional sequence/fallback and
    must be in [0, len(children)]. Default value is (-1) means len(children)

    if #success = succes_threshold, return a success

    if #failure = len(children) - succes_threshold, return a failure

    What we can return as value and keep sematic Failure/Success:
     - an array of previous result when success
     - last failure when fail

    Args:
        children (list[CallableFunction]): list of Awaitable
        succes_threshold (int): succes threshold value

    Returns:
        (AsyncInnerFunction): an awaitable function.

    Raises:
        (AssertionError): if succes_threshold is invalid
    """
    _succes_threshold = succes_threshold or len(children)
    if not (0 <= _succes_threshold <= len(children)):
        raise AssertionError("succes_threshold")

    failure_threshold = len(children) - _succes_threshold + 1

    _children = [to_async(child) for child in children]

    @node_metadata(properties=["_succes_threshold"])
    async def _sequence():
        success = 0
        failure = 0
        results = []

        for child in _children:
            last_result = await child()
            results.append(last_result)

            if bool(last_result):
                success += 1
                if success == _succes_threshold:
                    # last evaluation is a success
                    return results
            else:
                failure += 1
                if failure == failure_threshold:
                    # last evaluation is a failure
                    return last_result
        # should be never reached
        return FAILURE

    return _sequence


def fallback(children: list[CallableFunction]) -> AsyncInnerFunction:
    """Execute tasks in sequence and succeed if one succeed or failed if all failed.

    Often named 'selector', children can be seen as an ordered list
        starting from higthest priority to lowest priority.

    Args:
        children (list[CallableFunction]): list of Awaitable

    Returns:
        (AsyncInnerFunction): an awaitable function.
    """
    return alias_node_metadata(
        name="fallback",
        target=sequence(children, succes_threshold=min(1, len(children))),
    )


def selector(children: list[CallableFunction]) -> AsyncInnerFunction:
    """Synonym of fallback."""
    return alias_node_metadata(
        name="selector",
        target=sequence(children, succes_threshold=min(1, len(children))),
    )


def decision(
    condition: CallableFunction,
    success_tree: CallableFunction,
    failure_tree: Optional[CallableFunction] = None,
) -> AsyncInnerFunction:
    """Create a decision node.

    If condition is meet, return evaluation of success_tree.
    Otherwise, it return SUCCESS or evaluation of failure_tree if setted.

    Args:
        condition (CallableFunction): awaitable condition
        success_tree (CallableFunction): awaitable success tree which be
            evaluated if cond is Truthy
        failure_tree (CallableFunction): awaitable failure tree which be
            evaluated if cond is Falsy (None per default)

    Returns:
        (AsyncInnerFunction): an awaitable function.
    """

    _condition = to_async(condition)
    _success_tree = to_async(success_tree)
    _failure_tree = to_async(failure_tree) if failure_tree else None

    @node_metadata(edges=["_condition", "_success_tree", "_failure_tree"])
    async def _decision():
        if bool(await _condition()):
            return await _success_tree()
        if _failure_tree:
            return await _failure_tree()
        return SUCCESS

    return _decision


def repeat_until(condition: CallableFunction, child: CallableFunction) -> AsyncInnerFunction:
    """Repeat child evaluation until condition is truthy.

    Return last child evaluation or FAILURE if no evaluation occurs.

    Args:
        condition (CallableFunction): awaitable condition
        child (CallableFunction): awaitable child

    Returns:
        (AsyncInnerFunction): an awaitable function.
    """

    _child = to_async(child)
    _condition = to_async(condition)

    @node_metadata(edges=["_condition", "_child"])
    async def _repeat_until():
        result: Any = FAILURE
        while bool(await _condition()):
            result = await _child()

        return result

    return _repeat_until
