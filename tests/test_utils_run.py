from contextvars import ContextVar

from curio import Kernel, run as _curio_run

from async_btree import run


def test_run_curio():
    counter = ContextVar("counter", default=5)

    async def reset_counter():
        if counter.get() == 5:
            counter.set(0)
            return 0
        return -1

    with Kernel() as kernel:
        assert run(kernel, reset_counter) == 0
        assert run(kernel, reset_counter) == 0
        assert counter.get() == 5

    assert _curio_run(reset_counter) == 0
    assert _curio_run(reset_counter) == -1
    assert counter.get() == 0
