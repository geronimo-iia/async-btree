"""Control function definition."""
from typing import Any, List, Optional

from .decorator import is_success
from .definition import FAILURE, AsyncInnerFunction, CallableFunction, node_metadata
from .utils import to_async

__all__ = ['sequence', 'fallback', 'selector', 'decision', 'repeat_until']


def sequence(children: List[CallableFunction], succes_threshold: int = -1) -> AsyncInnerFunction:
    """Return a function which execute children in sequence.

    succes_threshold parameter generalize traditional sequence/fallback and
    must be in [0, len(children)]. Default value is (-1) means len(children)

    if #success = succes_threshold, return a success

    if #failure = len(children) - succes_threshold, return a failure

    What we can return as value and keep sematic Failure/Success:
     - an array of previous result when success
     - last failure when fail

    Args:
        children (List[CallableFunction]): list of Awaitable
        succes_threshold (int): succes threshold value

    Returns:
        (AsyncInnerFunction): an awaitable function.

    Raises:
        (AssertionError): if succes_threshold is invalid
    """
    succes_threshold = succes_threshold if succes_threshold != -1 else len(children)
    if not (0 <= succes_threshold <= len(children)):
        raise AssertionError('succes_threshold')

    failure_threshold = len(children) - succes_threshold + 1

    _children = [to_async(child) for child in children]

    @node_metadata(properties=['succes_threshold'])
    async def _sequence():
        success = 0
        failure = 0
        results = []

        for child in _children:
            last_result = await child()
            results.append(last_result)

            if last_result:
                success += 1
                if success == succes_threshold:
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


def fallback(children: List[CallableFunction]) -> AsyncInnerFunction:
    """Execute tasks in sequence and succeed if one succeed or failed if all failed.

    Often named 'selector', children can be seen as an ordered list
        starting from higthest priority to lowest priority.

    Args:
        children (List[CallableFunction]): list of Awaitable

    Returns:
        (AsyncInnerFunction): an awaitable function.
    """

    return node_metadata(name='fallback')(sequence(children, succes_threshold=min(1, len(children))))


def selector(children: List[CallableFunction]) -> AsyncInnerFunction:
    """Synonym of fallback."""
    return node_metadata(name='selector')(fallback(children))


def decision(
    condition: CallableFunction, success_tree: CallableFunction, failure_tree: Optional[CallableFunction] = None
) -> AsyncInnerFunction:
    """Create a decision node.

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

    @node_metadata(edges=['condition', 'success_tree', 'failure_tree'])
    async def _decision():
        if await _condition():
            return await _success_tree()
        if _failure_tree:
            return await _failure_tree()
        return FAILURE

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

    @node_metadata(edges=['condition', 'child'])
    async def _repeat_until():
        result: Any = FAILURE
        condition_eval = is_success(child=condition)
        while await condition_eval():
            result = await _child()

        return result

    return _repeat_until
