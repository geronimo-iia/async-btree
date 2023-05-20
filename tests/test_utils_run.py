# from asyncio import run as run_asyncio
from contextvars import ContextVar

from curio import Kernel

from async_btree.utils import run, run_curio, has_curio

counter = ContextVar("counter", default=5)


async def reset_counter():
    if counter.get() == 5:
        counter.set(0)
        return 0
    return -1


def test_run():
    assert run
    if has_curio():
        assert run == run_curio


def test_run_curio_with_separate_contextvar():

    with Kernel() as k:
        assert run_curio(k, reset_counter) == 0
        assert run_curio(k, reset_counter) == 0
        assert counter.get() == 5

    assert counter.get() == 5


# def test_run_asyncio_with_separate_contextvar():

#     # from asyncio import Runner only with python > 3.11
#     # with Runner() as k:
#     assert run_asyncio(reset_counter) == 0
#     assert run_asyncio(reset_counter) == 0
#     assert counter.get() == 5

#     assert counter.get() == 5
