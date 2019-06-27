from libellule.control_flow.common import FAILURE
from libellule.control_flow.curiosity import parallele, run as run_curio
from curio import run, sleep, Kernel
from contextvars import ContextVar


async def a_func():
    await sleep(1)
    return "a"


async def b_func():
    await sleep(3)
    return "b"


async def failure_func():
    await sleep(2)
    return FAILURE


def test_parallele():
    assert run(parallele(children=[a_func]))
    assert run(parallele(children=[a_func, b_func]))
    assert not run(parallele(children=[a_func, b_func, failure_func]))
    assert run(parallele(children=[a_func, b_func, failure_func], succes_threshold=2))


def test_run_curio():
    counter = ContextVar("counter", default=5)

    async def reset_counter():
        if counter.get() == 5:
            counter.set(0)
            return 0
        return -1

    with Kernel() as kernel:
        assert run_curio(kernel, reset_counter) == 0
        assert run_curio(kernel, reset_counter) == 0
        assert counter.get() == 5

    assert run(reset_counter) == 0
    assert run(reset_counter) == -1
    assert counter.get() == 0
