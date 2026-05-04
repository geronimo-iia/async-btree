from asyncio import Runner
from contextvars import ContextVar, copy_context

counter = ContextVar("counter", default=5)


async def reset_counter():
    if counter.get() == 5:
        counter.set(0)
        return 0
    return -1


def test_run_asyncio_with_separate_contextvar():
    counter.set(5)
    with Runner() as r:
        assert r.run(reset_counter(), context=copy_context()) == 0
        assert r.run(reset_counter(), context=copy_context()) == 0
        assert counter.get() == 5

    assert counter.get() == 5


def test_run_asyncio_with_same_contextvar():
    counter.set(5)
    ctx = copy_context()
    with Runner() as r:
        assert r.run(reset_counter(), context=ctx) == 0
        assert r.run(reset_counter(), context=ctx) == -1
        assert ctx.run(counter.get) == 0

    assert counter.get() == 5
