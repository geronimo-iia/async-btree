import sys
from collections.abc import Awaitable
from contextvars import Context, copy_context
from typing import Callable, ContextManager, Optional, TypeVar

from .utils import has_curio

R = TypeVar("R", covariant=True)

__all__ = ["BTreeRunner"]


class BTreeRunner:
    """A context manager that call multiple async btree function in same context from sync framework.

    `asyncio` provide a Runner (python >= 3.11) to call several top-level async functions in the SAME context.

    The goal here is to hide underlaying asyncio framework.

    This function cannot be called when another asyncio event loop is running in the same thread.

    This function always creates a new event loop or Kernel and closes it at the end.
    It should be used as a main entry point for asyncio programs, and should ideally only be called once.

    """

    def __init__(self, disable_curio: bool = False) -> None:
        """Create a runner to call ultiple async btree function in same context from existing sync framework.

        Args:
            disable_curio (bool, optional): Force usage of `asyncio` Defaults to False.

        Raises:
            RuntimeError: if python version is below 3.11 and disable_curio is set.
        """
        self._has_curio = has_curio() and not disable_curio
        self._context: Optional[Context] = None
        # curio support
        self._kernel: Optional[ContextManager] = None
        # asyncio support
        if not self._has_curio and sys.version_info.minor < 11:
            raise RuntimeError("asyncio support only for python 3.11")
        self._runner = None

    def __enter__(self):
        self._context = copy_context()

        if self._has_curio:
            from curio import Kernel

            self._kernel = Kernel()
        else:
            from asyncio import Runner  # pyright: ignore[reportAttributeAccessIssue]

            self._kernel = Runner()

        self._kernel.__enter__()  # type: ignore

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self._kernel.__exit__(exc_type, exc_value, traceback)  # type: ignore
        finally:
            self._kernel = None
            self._context = None

    def run(self, target: Callable[..., Awaitable[R]], *args, **kwargs) -> R:
        """Run an async btree coroutine in a same context.

        Args:
            target (Callable[..., Awaitable[R]]): coroutine

        Raises:
            RuntimeError: if context is not initialized

        Returns:
            R: result
        """
        if not self._kernel:
            raise RuntimeError("run method must be invoked inside a context.")
        coro = target(*args, **kwargs)
        if self._has_curio:
            return self._context.run(self._kernel.run, coro)  # type: ignore
        return self._kernel.run(coro, context=self._context)  # type: ignore
