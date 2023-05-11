"""Curiosity module define special construct with curio framework."""

from typing import List, Optional

# default to a simple sequence
from .control import sequence
from .definition import AsyncInnerFunction, CallableFunction, alias_node_metadata, node_metadata
from .utils import to_async

__all__ = ['parallele']


try:
    from curio import TaskGroup

    def parallele(children: List[CallableFunction], succes_threshold: Optional[int] = None) -> AsyncInnerFunction:
        """Return an awaitable function which run children in parallele.

        `succes_threshold` parameter generalize traditional sequence/fallback,
        and must be in [0, len(children)], default value is len(children)

        if #success = succes_threshold, return a success

        if #failure = len(children) - succes_threshold, return a failure

        Args:
            children (List[CallableFunction]): list of Awaitable
            succes_threshold (int): succes threshold value, default len(children)

        Returns:
            (AsyncInnerFunction): an awaitable function.

        """
        _succes_threshold = succes_threshold or len(children)
        if not (0 <= _succes_threshold <= len(children)):
            raise AssertionError('succes_threshold')

        _children = [to_async(child) for child in children]

        @node_metadata(properties=['_succes_threshold'])
        async def _parallele():

            async with TaskGroup(wait=all) as g:
                for child in _children:
                    await g.spawn(child)

            success = len(list(filter(bool, g.results)))

            return success >= _succes_threshold

        return _parallele

except Exception:  # pragma: no cover

    def parallele(children: List[CallableFunction], succes_threshold: Optional[int] = None) -> AsyncInnerFunction:
        return alias_node_metadata(
            name="parallele", target=sequence(children=children, succes_threshold=succes_threshold)
        )
