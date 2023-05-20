# from asyncio import run as run_asyncio
from contextvars import ContextVar, copy_context

from curio import Kernel

from async_btree.utils import has_curio

counter = ContextVar("counter", default=5)


async def reset_counter():
    if counter.get() == 5:
        counter.set(0)
        return 0
    return -1


def test_run_curio_with_separate_contextvar():
    counter.set(5)
    with Kernel() as k:
        assert copy_context().run(k.run, reset_counter) == 0
        assert copy_context().run(k.run, reset_counter) == 0
        assert counter.get() == 5

    assert counter.get() == 5


def test_run_curio_with_same_contextvar():
    counter.set(5)
    with Kernel() as k:
        assert k.run(reset_counter) == 0
        assert k.run(reset_counter) == -1
        assert counter.get() == 0

    assert counter.get() == 0


def test_has_curio():
    assert has_curio()
