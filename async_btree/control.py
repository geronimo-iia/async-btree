"""Control function definition."""
from typing import Any, List, Optional

from .decorator import is_success
from .definition import (
    FAILURE,
    AsyncInnerFunction,
    CallableFunction,
    ExceptionDecorator,
    node_metadata,
)


__all__ = ['sequence', 'fallback', 'selector', 'decision', 'repeat_until']


def sequence(
    children: List[CallableFunction], succes_threshold: int = -1
) -> AsyncInnerFunction:
    """
    'sequence' return a function which execute children in sequence.

    succes_threshold generalize traditional sequence/fallback.
    succes_threshold must be in [0, len(children)],
        is default value is (-1) means len(children)

    if #success = succes_threshold, return a success

    if #failure = len(children) - succes_threshold, return a failure

    What we can return as value and keep sematic Failure/Success:
     - an array of previous result when success
     - last failure when fail

    :param children: list of Awaitable
    :param succes_threshold: succes threshold value
    :return: an awaitable function.
    """
    succes_threshold = succes_threshold if succes_threshold != -1 else len(children)
    assert 0 <= succes_threshold <= len(children)
    failure_threshold = len(children) - succes_threshold + 1

    @node_metadata(properties=['succes_threshold'])
    async def _sequence():
        success = 0
        failure = 0
        results = []

        for child in children:
            try:
                last_result = await child()
            except Exception as e:
                last_result = ExceptionDecorator(e)

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

    :param children: list of Awaitable
    :return: an awaitable function.
    """

    # @node_metadata()
    # async def _fallback():
    #    return sequence(children, succes_threshold=1)()

    return node_metadata(name='fallback')(
        sequence(children, succes_threshold=min(1, len(children)))
    )


def selector(children: List[CallableFunction]) -> AsyncInnerFunction:
    """Synonym of fallback."""
    return node_metadata(name='selector')(fallback(children))


def decision(
    condition: CallableFunction,
    success_tree: CallableFunction,
    failure_tree: Optional[CallableFunction] = None,
) -> AsyncInnerFunction:
    """Create a decision node.

    :param condition: awaitable condition
    :param success_tree: awaitable success tree which be evaluated if cond is Truthy
    :param failure_tree: awaitable failure tree  which be evaluated if cond is Falsy
        (None per default)
    :return: an awaitable function.
    """

    @node_metadata(edges=['condition', 'success_tree', 'failure_tree'])
    async def _decision():
        if await condition():
            return await success_tree()
        return await failure_tree() if failure_tree else FAILURE

    return _decision


def repeat_until(
    condition: CallableFunction, child: CallableFunction
) -> AsyncInnerFunction:
    """Repeat child evaluation until condition is truthy.

    Return last child evaluation or FAILURE if no evaluation occurs.
    :param condition: awaitable condition
    :param child: awaitable child
    :return: an awaitable function.
    """

    @node_metadata(edges=['condition', 'child'])
    async def _repeat_until():
        result: Any = FAILURE
        condition_eval = is_success(child=condition)
        while await condition_eval():
            try:
                result = await child()

            except Exception as e:
                result = ExceptionDecorator(e)

        return result

    return _repeat_until
