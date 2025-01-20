"""Curiosity module define special construct with curio framework."""

from asyncio import gather
from typing import Optional

# default to a simple sequence
from .control import sequence
from .definition import (
    AsyncCallableFunction,
    AsyncInnerFunction,
    CallableFunction,
    alias_node_metadata,
    node_metadata,
)
from .utils import has_curio, to_async

__all__ = ["parallele"]


def parallele(children: list[CallableFunction], succes_threshold: Optional[int] = None) -> AsyncInnerFunction:
    """Return an awaitable function which run children in parallele (Concurrently).

    `succes_threshold` parameter generalize traditional sequence/fallback,
    and must be in [0, len(children)], default value is len(children)

    if #success = succes_threshold, return a success

    if #failure = len(children) - succes_threshold, return a failure

    Args:
        children (list[CallableFunction]): list of Awaitable
        succes_threshold (int): succes threshold value, default len(children)

    Returns:
        (AsyncInnerFunction): an awaitable function.

    """
    _succes_threshold = succes_threshold or len(children)
    if not (0 <= _succes_threshold <= len(children)):
        raise AssertionError("succes_threshold")

    _parallele_implementation = parallele_curio if has_curio() else parallele_asyncio

    return _parallele_implementation(
        children=[to_async(child) for child in children],
        succes_threshold=_succes_threshold,
    )


try:
    from curio import TaskGroup

    def parallele_curio(children: list[AsyncCallableFunction], succes_threshold: int) -> AsyncInnerFunction:
        """Return an awaitable function which run children in parallele (Concurrently).

        Args:
            children (list[CallableFunction]): list of Awaitable
            succes_threshold (int): succes threshold value, default len(children)

        Returns:
            (AsyncInnerFunction): an awaitable function.

        """

        @node_metadata(properties=["succes_threshold"])
        async def _parallele():
            async with TaskGroup(wait=all) as g:
                for child in children:
                    await g.spawn(child)

            success = len(list(filter(bool, g.results)))

            return success >= succes_threshold

        return _parallele

except Exception:  # pragma: no cover

    def parallele_curio(children: list[AsyncCallableFunction], succes_threshold: int) -> AsyncInnerFunction:
        return alias_node_metadata(
            name="parallele",
            target=sequence(children=children, succes_threshold=succes_threshold),
        )


def parallele_asyncio(children: list[AsyncCallableFunction], succes_threshold: int) -> AsyncInnerFunction:
    """Return an awaitable function which run children in parallele (Concurrently).

    Args:
        children (list[CallableFunction]): list of Awaitable
        succes_threshold (int): succes threshold value, default len(children)

    Returns:
        (AsyncInnerFunction): an awaitable function.

    """

    @node_metadata(properties=["succes_threshold"])
    async def _parallele():
        results = await gather(*[child() for child in children], return_exceptions=True)
        success = len(list(filter(bool, results)))
        return success >= succes_threshold

    return _parallele
