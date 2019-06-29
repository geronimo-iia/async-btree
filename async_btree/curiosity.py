"""
Curiosity module define special construct with curio framework.
"""
from contextvars import copy_context
from typing import Awaitable, List

from curio import gather, spawn

from .common import FAILURE, SUCCESS, amap, node_metadata


__all__ = ['run', 'parallele']


def run(kernel, target, *args):
    """ Curio run with independent contextvars. """
    return copy_context().run(kernel.run, target, *args)


def parallele(children: List[Awaitable], succes_threshold: int = None) -> Awaitable:
    """
    Return an awaitable function which run children in parallele.

    succes_threshold generalize traditional sequence/fallback.
    succes_threshold must be in [0, len(children)], is default value is len(children)

    if #success = succes_threshold, return a success

    if #failure = len(children) - succes_threshold, return a failure

    :param children: list of Awaitable
    :param succes_threshold: succes threshold value
    :return: an awaitable function.

    """
    succes_threshold = succes_threshold if succes_threshold else len(children)
    assert 0 <= succes_threshold <= len(children)

    @node_metadata(properties=["succes_threshold"])
    async def _parallele():

        results = await gather([task async for task in amap(spawn, children)])

        success = len(list(filter(bool, results)))

        return SUCCESS if success >= succes_threshold else FAILURE

    return _parallele
