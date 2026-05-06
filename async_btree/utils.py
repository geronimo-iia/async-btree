"""Utility function."""

from __future__ import annotations

from collections.abc import AsyncGenerator, AsyncIterable, Awaitable, Callable, Iterable
from functools import wraps
from inspect import iscoroutinefunction
from typing import Any, TypeVar

from .definition import CallableFunction, node_metadata
from .runner import Backend, BTreeRunner

__all__ = ["afilter", "amap", "run", "run_once", "to_async"]

T = TypeVar("T")


async def amap(corofunc: Callable[[Any], Awaitable[T]], iterable: AsyncIterable | Iterable) -> AsyncGenerator[T, None]:
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
    corofunc: Callable[[Any], Awaitable[bool]], iterable: AsyncIterable | Iterable
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
    """Return `target` unchanged if already async, otherwise wrap it in an async function.

    The returned wrapper carries `__node_metadata` with the original function's name,
    so sync functions participate in tree introspection via `analyze()`.

    Args:
        target (CallableFunction): sync or async callable.

    Returns:
        (Callable[..., Awaitable[Any]]): an async version of `target`.
    """
    if iscoroutinefunction(target):
        return target

    @node_metadata(name=target.__name__.lstrip("_") if hasattr(target, "__name__") else "anonymous")
    async def _to_async(*args: Any, **kwargs: Any) -> Any:
        return target(*args, **kwargs)

    return _to_async


def run_once(target: CallableFunction) -> CallableFunction:
    """Implement 'run once' function.

    The target function is called exactly once. Any further call will return the first result.
    This decorator works on async and sync functions.

    Args:
        target (CallableFunction): target function

    Returns:
        CallableFunction: decorated run once function.
    """
    _result = None
    _has_run = False

    if not iscoroutinefunction(target):

        @wraps(target)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            nonlocal _result, _has_run
            if not _has_run:
                _has_run = True
                _result = target(*args, **kwargs)
            return _result

        return sync_wrapper

    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        nonlocal _result, _has_run
        if not _has_run:
            _has_run = True
            _result = await target(*args, **kwargs)  # type: ignore[misc]
        return _result

    return async_wrapper


def run(
    target: Callable[..., Awaitable[Any]],
    *args: Any,
    backend: Backend = "asyncio",
    **kwargs: Any,
) -> Any:
    """Run a behavior tree callable to completion.

    Convenience wrapper around BTreeRunner for one-shot execution.

    Args:
        target: async callable (coroutine function)
        *args: positional arguments passed to target
        backend: async runtime — "asyncio" (default), "trio", or "asyncio+uvloop"
        **kwargs: keyword arguments passed to target

    Returns:
        whatever target returns
    """
    with BTreeRunner(backend=backend) as runner:
        return runner.run(target, *args, **kwargs)
