"""Curiosity module define special construct with curio framework."""

from typing import List

from .definition import FAILURE, SUCCESS, AsyncInnerFunction, CallableFunction, node_metadata
from .utils import amap

__all__ = ['parallele']


try:
    from curio import gather, spawn

    def parallele(children: List[CallableFunction], succes_threshold: int = -1) -> AsyncInnerFunction:
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
        succes_threshold = succes_threshold if succes_threshold != -1 else len(children)
        if not (0 <= succes_threshold <= len(children)):
            raise AssertionError('succes_threshold')

        @node_metadata(properties=['succes_threshold'])
        async def _parallele():

            results = await gather([task async for task in amap(spawn, children)])

            success = len(list(filter(bool, results)))

            return SUCCESS if success >= succes_threshold else FAILURE

        return _parallele


except Exception:  # pragma: no cover
    # default to a simple sequence
    from .control import sequence as parallele
