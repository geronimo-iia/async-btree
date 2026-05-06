"""Control function definition."""

import random
from typing import Any

from .definition import (
    FAILURE,
    SUCCESS,
    AsyncInnerFunction,
    CallableFunction,
    alias_node_metadata,
    node_metadata,
)
from .utils import to_async

__all__ = [
    "condition_guard",
    "decision",
    "do_while",
    "fallback",
    "random_selector",
    "repeat_n",
    "repeat_until",
    "repeat_while",
    "selector",
    "sequence",
    "switch",
]


def sequence(children: list[CallableFunction], success_threshold: int | None = None) -> AsyncInnerFunction:
    """Return a function which executes children in sequence.

    `success_threshold` generalizes traditional sequence/fallback behaviour and
    must be in `[0, len(children)]`. Defaults to `None`, which means `len(children)`
    (all children must succeed).

    - If #success reaches `success_threshold`, returns the list of results collected so far.
    - If #failure reaches `len(children) - success_threshold + 1`, returns the last falsy result.

    Args:
        children (list[CallableFunction]): list of sync or async callables.
        success_threshold (int | None): minimum number of children that must succeed.
            Defaults to `None` (equivalent to `len(children)`).

    Returns:
        (AsyncInnerFunction): an awaitable function that returns a list of results on
            success, or the last falsy result on failure.

    Raises:
        AssertionError: if `success_threshold` is outside `[0, len(children)]`.
    """
    _success_threshold = success_threshold if success_threshold is not None else len(children)
    if not (0 <= _success_threshold <= len(children)):
        raise AssertionError("success_threshold")

    failure_threshold = len(children) - _success_threshold + 1

    _children = [to_async(child) for child in children]

    @node_metadata(properties=["_success_threshold"])
    async def _sequence():
        success = 0
        failure = 0
        results = []

        for child in _children:
            last_result = await child()
            results.append(last_result)

            if bool(last_result):
                success += 1
                if success == _success_threshold:
                    return results
            else:
                failure += 1
                if failure == failure_threshold:
                    return last_result
        return FAILURE

    return _sequence


def fallback(children: list[CallableFunction]) -> AsyncInnerFunction:
    """Execute children in sequence and succeed as soon as one succeeds; fail if all fail.

    Children are evaluated in order from highest to lowest priority. Evaluation stops
    at the first truthy result. `selector` is an alias for this function.

    Args:
        children (list[CallableFunction]): list of sync or async callables.

    Returns:
        (AsyncInnerFunction): an awaitable function that returns the first truthy result,
            or the last falsy result if all children fail.
    """
    return alias_node_metadata(
        name="fallback",
        target=sequence(children, success_threshold=min(1, len(children))),
    )


def selector(children: list[CallableFunction]) -> AsyncInnerFunction:
    """Alias of `fallback`. Execute children in sequence and succeed as soon as one succeeds.

    Children are evaluated in order from highest to lowest priority. Evaluation stops
    at the first truthy result.

    Args:
        children (list[CallableFunction]): list of sync or async callables.

    Returns:
        (AsyncInnerFunction): an awaitable function that returns the first truthy result,
            or the last falsy result if all children fail.
    """
    return alias_node_metadata(
        name="selector",
        target=sequence(children, success_threshold=min(1, len(children))),
    )


def decision(
    condition: CallableFunction,
    success_tree: CallableFunction,
    failure_tree: CallableFunction | None = None,
) -> AsyncInnerFunction:
    """Create a decision node.

    If condition is truthy, return evaluation of `success_tree`.
    Otherwise, return evaluation of `failure_tree` if set, or `SUCCESS`.

    Args:
        condition (CallableFunction): sync or async callable evaluated as a boolean.
        success_tree (CallableFunction): callable evaluated when condition is truthy.
        failure_tree (CallableFunction | None): callable evaluated when condition is falsy.
            Defaults to `None`; when absent, returns `SUCCESS`.

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


def condition_guard(condition: CallableFunction, child: CallableFunction) -> AsyncInnerFunction:
    """Run child only if condition is truthy; return SUCCESS without running child if condition is falsy.

    Semantic shorthand for `decision(condition, success_tree=child)` with no failure tree.

    Args:
        condition (CallableFunction): sync or async callable evaluated as a boolean.
        child (CallableFunction): callable run only when condition is truthy.

    Returns:
        (AsyncInnerFunction): an awaitable function that returns child result when condition
            is truthy, or `SUCCESS` when condition is falsy.
    """
    return alias_node_metadata(name="condition_guard", target=decision(condition=condition, success_tree=child))


def repeat_while(condition: CallableFunction, child: CallableFunction) -> AsyncInnerFunction:
    """Repeat child while condition is truthy, stopping when condition becomes falsy.

    Returns the last child evaluation, or `FAILURE` if condition is falsy on the first check.

    Args:
        condition (CallableFunction): sync or async callable evaluated before each iteration.
        child (CallableFunction): sync or async callable executed each iteration.

    Returns:
        (AsyncInnerFunction): an awaitable function.
    """

    _child = to_async(child)
    _condition = to_async(condition)

    @node_metadata(edges=["_condition", "_child"])
    async def _repeat_while():
        result: Any = FAILURE
        while bool(await _condition()):
            result = await _child()

        return result

    return _repeat_while


def repeat_until(condition: CallableFunction, child: CallableFunction) -> AsyncInnerFunction:
    """Repeat child until condition becomes truthy, stopping when condition is met.

    Returns the last child evaluation, or `FAILURE` if condition is truthy on the first check
    (no iteration occurs).

    Args:
        condition (CallableFunction): sync or async callable evaluated before each iteration.
        child (CallableFunction): sync or async callable executed each iteration.

    Returns:
        (AsyncInnerFunction): an awaitable function.
    """

    _child = to_async(child)
    _condition = to_async(condition)

    @node_metadata(edges=["_condition", "_child"])
    async def _repeat_until():
        result: Any = FAILURE
        while not bool(await _condition()):
            result = await _child()

        return result

    return _repeat_until


def do_while(child: CallableFunction, condition: CallableFunction) -> AsyncInnerFunction:
    """Run child at least once, then repeat while condition is truthy.

    Unlike `repeat_while`, the child always executes at least once before the condition
    is checked.

    Args:
        child (CallableFunction): sync or async callable executed each iteration.
        condition (CallableFunction): sync or async callable checked after each iteration.

    Returns:
        (AsyncInnerFunction): an awaitable function that returns the last child result.
    """
    _child = to_async(child)
    _condition = to_async(condition)

    @node_metadata(edges=["_child", "_condition"])
    async def _do_while():
        result: Any = FAILURE
        while True:
            result = await _child()
            if not bool(await _condition()):
                break
        return result

    return _do_while


def repeat_n(child: CallableFunction, n: int) -> AsyncInnerFunction:
    """Run child exactly `n` times regardless of its result.

    Args:
        child (CallableFunction): sync or async callable to run.
        n (int): number of times to execute child.

    Returns:
        (AsyncInnerFunction): an awaitable function that returns the last child result,
            or `FAILURE` if `n` is 0.
    """
    _child = to_async(child)

    @node_metadata(properties=["n"])
    async def _repeat_n():
        result: Any = FAILURE
        for _ in range(n):
            result = await _child()
        return result

    return _repeat_n


def random_selector(children: list[CallableFunction]) -> AsyncInnerFunction:
    """Execute children in a random order, succeeding as soon as one succeeds.

    Children are reshuffled on every call, so the evaluation order differs each tick.

    Args:
        children (list[CallableFunction]): list of sync or async callables.

    Returns:
        (AsyncInnerFunction): an awaitable function that returns `[result]` for the first
            truthy child, or `FAILURE` if all children fail.
    """
    _children = [to_async(child) for child in children]

    @node_metadata()
    async def _random_selector():
        for child in random.sample(_children, len(_children)):
            result = await child()
            if bool(result):
                return [result]
        return FAILURE

    return _random_selector


def switch(
    condition: CallableFunction,
    cases: dict[Any, CallableFunction],
    default: CallableFunction | None = None,
) -> AsyncInnerFunction:
    """Route to a child based on the return value of `condition`.

    Evaluates `condition` to get a key, looks it up in `cases`, and runs the
    matching child. Falls back to `default` if no case matches. Returns `FAILURE`
    if no case matches and no default is provided.

    The case keys are shown in `stringify_analyze` output. The children themselves
    are not traversed by `analyze()`.

    Args:
        condition (CallableFunction): sync or async callable that returns a hashable key.
        cases (dict[Any, CallableFunction]): mapping of key → child callable.
        default (CallableFunction | None): callable run when no case matches. Defaults to `None`.

    Returns:
        (AsyncInnerFunction): an awaitable function that returns the matched child's result,
            or `FAILURE` if no match and no default.
    """
    _condition = to_async(condition)
    _cases = {k: to_async(v) for k, v in cases.items()}
    _default = to_async(default) if default else None
    _case_keys = list(cases.keys())

    @node_metadata(properties=["_case_keys"], edges=["_default"])
    async def _switch():
        _ = _case_keys  # ensure captured in closure for analyze()
        key = await _condition()
        child = _cases.get(key, _default)
        if child is None:
            return FAILURE
        return await child()

    return _switch
