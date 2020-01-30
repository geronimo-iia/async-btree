from contextvars import ContextVar

from curio import Kernel

from async_btree import run


def test_run_curio(kernel):
    counter = ContextVar("counter", default=5)

    async def reset_counter():
        if counter.get() == 5:
            counter.set(0)
            return 0
        return -1

    with Kernel() as k:
        assert run(k, reset_counter) == 0
        assert run(k, reset_counter) == 0
        assert counter.get() == 5

    assert kernel.run(reset_counter) == 0
    assert kernel.run(reset_counter) == -1
    assert counter.get() == 0
