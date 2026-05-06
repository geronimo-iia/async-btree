from __future__ import annotations

import contextvars
from contextvars import copy_context
from typing import TYPE_CHECKING, Any, Literal, TypeVar

import anyio

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

Backend = Literal["asyncio", "trio", "asyncio+uvloop"]

_BACKEND_MAP: dict[Backend, tuple[str, dict[str, Any] | None]] = {
    "asyncio": ("asyncio", None),
    "trio": ("trio", None),
    "asyncio+uvloop": ("asyncio", {"use_uvloop": True}),
}

R = TypeVar("R")

__all__ = ["BTreeRunner", "Backend"]


class BTreeRunner:
    """Context manager that runs behavior trees against a configurable async backend.

    On `__enter__`, a snapshot of the caller's `ContextVar` state is captured via
    `copy_context()`. Each `run()` call executes in an isolated copy of that snapshot —
    mutations inside a run do not escape to the caller and do not accumulate across
    successive `run()` calls.

    Args:
        backend (Backend): async runtime to use — "asyncio" (default), "trio", or
            "asyncio+uvloop".
    """

    def __init__(self, backend: Backend = "asyncio") -> None:
        self._anyio_backend, self._anyio_backend_options = _BACKEND_MAP[backend]
        self._context: contextvars.Context | None = None

    def __enter__(self) -> BTreeRunner:
        self._context = copy_context()
        return self

    def __exit__(self, *_: Any) -> None:
        self._context = None

    def run(self, target: Callable[..., Awaitable[R]], *args: Any, **kwargs: Any) -> R:
        """Run an async callable to completion using the configured backend.

        Must be called within a `with BTreeRunner() as runner:` block.

        Each call runs in an isolated copy of the context captured at `__enter__`.
        ContextVar mutations inside `target` do not escape to the caller and do not
        accumulate across successive `run()` calls.

        Args:
            target: async callable (coroutine function)
            *args: positional arguments passed to target
            **kwargs: keyword arguments passed to target

        Returns:
            whatever target returns

        Raises:
            RuntimeError: if called outside of the context manager
        """
        if self._context is None:
            raise RuntimeError("BTreeRunner.run() must be called within a 'with' block")
        return self._context.run(
            anyio.run, target, *args, backend=self._anyio_backend, backend_options=self._anyio_backend_options, **kwargs
        )
