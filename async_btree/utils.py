"""Utility function."""

from collections.abc import AsyncGenerator, AsyncIterable, Awaitable, Iterable
from contextvars import copy_context
from functools import wraps
from inspect import iscoroutinefunction
from typing import Any, Callable, TypeVar, Union
from warnings import warn

from .definition import CallableFunction, node_metadata

__all__ = ["amap", "afilter", "run", "to_async", "has_curio", "run_once"]

T = TypeVar("T")


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
    if isinstance(iterable, AsyncIterable):
        async for item in iterable:
            yield await corofunc(item)
    else:
        for item in iterable:
            yield await corofunc(item)


async def afilter(
    corofunc: Callable[[Any], Awaitable[bool]], iterable: Union[AsyncIterable, Iterable]
) -> AsyncGenerator[Any, None]:
    """Filter an iterable or an async iterable with an async function.

    This simplify writing of filtering by a function on something iterable
    between 'async for ...' and 'for...' .

    Args:
        corofunc (Callable[[Any], Awaitable[bool]]): filter async function
        iterable (Union[AsyncIterable, Iterable]): iterable or async iterable collection
            which will be applied.

    Returns:
        (AsyncGenerator[Any]): an async iterator of item which satisfy corofunc(item) == True

    Example:
        ```[i async for i in amap(inc, afilter(even, [0, 1, 2, 3, 4]))]```

    """
    if isinstance(iterable, AsyncIterable):
        async for item in iterable:
            if await corofunc(item):
                yield item
    else:
        for item in iterable:
            if await corofunc(item):
                yield item


def to_async(target: CallableFunction) -> Callable[..., Awaitable[Any]]:
    """Transform target function in async function if necessary.

    Args:
        target (CallableFunction): function to transform in async if necessary

    Returns:
        (Callable[..., Awaitable[Any]]): an async version of target function
    """

    if iscoroutinefunction(target):
        # nothing todo
        return target

    # use node_metadata to keep trace of target function name
    @node_metadata(name=target.__name__.lstrip("_") if hasattr(target, "__name__") else "anonymous")
    async def _to_async(*args, **kwargs):
        return target(*args, **kwargs)

    return _to_async


def run_once(target: CallableFunction) -> CallableFunction:
    """Implemet 'run once' function.

    The target function is call exactly once. Any fuher call will return the first result.
    This decorator works on async and sync function.

    Args:
        target (CallableFunction): target function

    Returns:
        CallableFunction: decorated run once function.
    """
    _result = None
    _has_run = False

    if not iscoroutinefunction(target):

        @wraps(target)
        def sync_wrapper(*args, **kwargs):
            nonlocal _result, _has_run
            if not _has_run:
                _has_run = True
                _result = target(*args, **kwargs)
            return _result

        return sync_wrapper

    async def async_wrapper(*args, **kwargs):
        nonlocal _result, _has_run
        if not _has_run:
            _has_run = True
            _result = await target(*args, **kwargs)
        return _result

    return async_wrapper


@run_once
def has_curio() -> bool:
    """Return True if curio extention is present.

    Returns:
        bool:  True if curio extention is present.
    """
    try:
        import curio  # noqa: F401

        return True
    except Exception:  # pragma: no cover
        return False


def run(kernel, target, *args):
    """Curio run with independent contextvars.

    This mimic asyncio framework behaviour.
    We use a contextvars per run rather than use one per task with `from curio.task.ContextTask`

    ```
    copy_context().run(kernel.run, target, *args)
    ```

    """
    warn("This method is deprecated.", DeprecationWarning, stacklevel=2)
    return copy_context().run(kernel.run, target, *args)
