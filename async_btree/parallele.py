from __future__ import annotations

from typing import Any

import anyio

from .definition import (
    FAILURE,
    AsyncInnerFunction,
    CallableFunction,
    ControlFlowException,
    node_metadata,
)
from .utils import to_async

__all__ = ["parallel_race", "parallele"]


def parallele(
    children: list[CallableFunction],
    success_threshold: int | None = None,
) -> AsyncInnerFunction:
    """Return an awaitable function which runs children concurrently.

    `success_threshold` generalizes sequence/fallback:
    must be in [0, len(children)], default is len(children).

    If #success >= success_threshold, return SUCCESS.
    If #failure >= len(children) - success_threshold, return FAILURE.

    Args:
        children: list of sync or async callables
        success_threshold: minimum successes required, default len(children)

    Returns:
        AsyncInnerFunction: an awaitable function
    """
    _success_threshold = success_threshold if success_threshold is not None else len(children)
    if not (0 <= _success_threshold <= len(children)):
        raise AssertionError("success_threshold must be in [0, len(children)]")

    _children = [to_async(child) for child in children]

    @node_metadata(properties=["success_threshold"])
    async def _parallele() -> bool:
        results: list[Any] = []

        async def _run(child: AsyncInnerFunction) -> None:
            results.append(await child())

        try:
            async with anyio.create_task_group() as tg:
                for child in _children:
                    tg.start_soon(_run, child)

            return len(list(filter(bool, results))) >= _success_threshold
        except Exception as e:
            raise ControlFlowException.instantiate(e) from e

    return _parallele


def parallel_race(children: list[CallableFunction]) -> AsyncInnerFunction:
    """Run children concurrently; return the result of the first child to finish.

    As soon as one child completes, all remaining children are cancelled.
    Returns `FAILURE` if `children` is empty.

    Args:
        children: list of sync or async callables.

    Returns:
        AsyncInnerFunction: an awaitable function that returns the winner's result.

    Raises:
        ControlFlowException: wrapping any exception raised by a child.
    """
    _children = [to_async(child) for child in children]

    @node_metadata()
    async def _parallel_race() -> Any:
        winner: list[Any] = []

        async def _run(child: AsyncInnerFunction) -> None:
            result = await child()
            if not winner:
                winner.append(result)
                tg.cancel_scope.cancel()

        try:
            async with anyio.create_task_group() as tg:
                for child in _children:
                    tg.start_soon(_run, child)
        except Exception as e:
            raise ControlFlowException.instantiate(e) from e

        return winner[0] if winner else FAILURE

    return _parallel_race
