"""
Utility function.
"""
from typing import (
    Any,
    AsyncGenerator,
    AsyncIterable,
    Awaitable,
    Callable,
    Iterable,
    TypeVar,
    Union,
)

__all__ = ['amap','afilter']

T = TypeVar('T')


async def amap(
    corofunc: Awaitable[Callable[Any], T], iterable: Union[AsyncIterable, Iterable]
) -> AsyncGenerator[T]:
    """Map an async function onto an iterable or an async iterable.

    Parameters:
    corofunc (Awaitable[Callable[Any], T]): coroutine function
    iterable (Union[AsyncIterable, Iterable]): iterable or async iterable collection which will be applied.

    Returns:
    AsyncGenerator[T]: an async iterator of corofunc(item)

    Example:
        [i async for i in amap(inc, afilter(even, [0, 1, 2, 3, 4]))]
    """
    if hasattr(iterable, '__aiter__'):
        async for item in iterable:
            yield await corofunc(item)
    else:
        for item in iterable:
            yield await corofunc(item)


async def afilter(
    corofunc: Awaitable[Callable[T], bool], iterable: Union[AsyncIterable, Iterable]
) -> AsyncGenerator[T]:
    """Filter an iterable or an async iterable with an async function.

    :param corofunc: coroutine function (item) -> bool
    :param iterable: iterable or async iterable collection which will be applied.
    :return: an async iterator of item which satisfy corofunc(item) == True
    """
    if hasattr(iterable, '__aiter__'):
        async for item in iterable:
            if await corofunc(item):
                yield item
    else:
        for item in iterable:
            if await corofunc(item):
                yield item
