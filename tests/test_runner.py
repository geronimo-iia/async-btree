import sys
from contextvars import ContextVar

import pytest

from async_btree import BTreeRunner

counter = ContextVar("counter", default=5)


async def a_func():
    return "a"


async def inc(i):
    return i + 1


async def dec_counter():
    counter.set(counter.get() - 1)
    return counter.get() > 0


def test_curio_runner():
    with BTreeRunner() as r:
        assert r.run(a_func) == "a"
        assert r.run(inc, 2) == 3


def test_asyncio_runner():
    if sys.version_info.minor < 11:
        with pytest.raises(RuntimeError), BTreeRunner(disable_curio=True) as r:
            assert r.run(a_func) == "a"
            assert r.run(inc, 2) == 3
    else:
        with BTreeRunner(disable_curio=True) as r:
            assert r.run(a_func) == "a"
            assert r.run(inc, 2) == 3


def _check_sequence(runner: BTreeRunner):
    with runner:
        assert runner.run(dec_counter)
        assert runner.run(dec_counter)
        assert runner.run(dec_counter)
        assert runner.run(dec_counter)
        assert not runner.run(dec_counter)


def test_curio_runner_share_context():
    counter.set(5)
    _check_sequence(runner=BTreeRunner())

    # we did not affect man context
    assert counter.get() == 5

    _check_sequence(runner=BTreeRunner())


def test_asyncio_runner_share_context():
    counter.set(5)

    if sys.version_info.minor < 11:
        with pytest.raises(RuntimeError), BTreeRunner(disable_curio=True) as r:
            assert r.run(a_func) == "a"
    else:
        _check_sequence(runner=BTreeRunner(disable_curio=True))
        assert counter.get() == 5
        _check_sequence(runner=BTreeRunner(disable_curio=True))
