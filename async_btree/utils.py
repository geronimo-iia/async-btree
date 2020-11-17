"""Utility function."""
from inspect import iscoroutinefunction
from typing import Any, AsyncGenerator, AsyncIterable, Awaitable, Callable, Iterable, TypeVar, Union

from .definition import CallableFunction

__all__ = ['amap', 'afilter', 'run', 'iscoroutinefunction', 'to_async']

T = TypeVar('T')


async def amap(
    corofunc: Callable[[Any], Awaitable[T]], iterable: Union[AsyncIterable, Iterable]
) -> AsyncGenerator[T, None]:
    """Map an async function onto an iterable or an async iterable.

    This simplify writing of mapping a function on something iterable
    between 'async for ...' and 'for...' .

    Args:
        corofunc (Callable[[Any], Awaitable[T]]): coroutine function
        iterable (Union[AsyncIterable, Iterable]): iterable or async iterable collection
            which will be applied.

    Returns:
        AsyncGenerator[T]: an async iterator of corofunc(item)

    Example:
        ```[i async for i in amap(inc, afilter(even, [0, 1, 2, 3, 4]))]```

    """
    if isinstance(iterable, AsyncIterable):  # if hasattr(iterable, '__aiter__'):
        async for item in iterable:
            yield await corofunc(item)
    else:
        for item in iterable:
            yield await corofunc(item)


async def afilter(
    corofunc: Callable[[Any], Awaitable[bool]], iterable: Union[AsyncIterable, Iterable]
) -> AsyncGenerator[T, None]:
    """Filter an iterable or an async iterable with an async function.

    This simplify writing of filtering by a function on something iterable
    between 'async for ...' and 'for...' .

    Args:
        corofunc (Callable[[Any], Awaitable[bool]]): filter async function
        iterable (Union[AsyncIterable, Iterable]): iterable or async iterable collection
            which will be applied.

    Returns:
        (AsyncGenerator[T]): an async iterator of item which satisfy corofunc(item) == True

    Example:
        ```[i async for i in amap(inc, afilter(even, [0, 1, 2, 3, 4]))]```

    """
    if isinstance(iterable, AsyncIterable):  # if hasattr(iterable, '__aiter__'):
        async for item in iterable:
            if await corofunc(item):
                yield item
    else:
        for item in iterable:
            if await corofunc(item):
                yield item


def to_async(func: CallableFunction) -> Callable[..., Awaitable[Any]]:
    async def _func(*args, **kwargs):
        return func(*args, **kwargs)

    return func if iscoroutinefunction(func) else _func


try:
    # TOOD this is not ncessary with curio 1.4
    import curio  # noqa: F401
    from contextvars import copy_context

    def run(kernel, target, *args):
        """Curio run with independent contextvars.

        This mimic asyncio framework behaviour.

        ```
        copy_context().run(kernel.run, target, *args)
        ```

        """
        return copy_context().run(kernel.run, target, *args)


except Exception:  # pragma: no cover

    def run(kernel, target, *args):
        raise RuntimeError('curio not installed!')
