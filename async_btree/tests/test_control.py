from libellule.control_flow.common import *
from libellule.control_flow.control import *
from curio import run
from contextvars import ContextVar


async def a_func():
    return "a"


async def b_func():
    return "b"


async def failure_func():
    return FAILURE


async def success_func():
    return SUCCESS


async def exception_func():
    raise RuntimeError()


def test_sequence():
    assert not run(
        sequence(children=[a_func, failure_func, success_func])
    ), "default behaviour fail of one failed"

    assert run(
        sequence(children=[a_func, failure_func, success_func], succes_threshold=2)
    )
    assert run(
        sequence(children=[a_func, success_func, failure_func], succes_threshold=2)
    )
    assert run(
        sequence(children=[failure_func, a_func, success_func], succes_threshold=2)
    )

    assert run(
        sequence(children=[exception_func, failure_func, a_func], succes_threshold=1)
    )
    assert not run(
        sequence(children=[exception_func, failure_func], succes_threshold=1)
    )

    assert not run(sequence(children=[]))


def test_fallback():
    assert run(fallback(children=[exception_func, failure_func, a_func]))
    assert not run(fallback(children=[exception_func, failure_func]))
    assert not run(fallback(children=[]))


def test_selector():
    assert run(selector(children=[exception_func, failure_func, a_func]))
    assert not run(selector(children=[exception_func, failure_func]))
    assert selector(children=[]).__node_metadata.name == "selector"


def test_decision():
    assert run(decision(condition=success_func, success_tree=a_func)) == "a"
    assert not run(decision(condition=failure_func, success_tree=a_func))
    assert (
        run(decision(condition=failure_func, success_tree=a_func, failure_tree=b_func))
        == "b"
    )


def test_repeat_until():

    counter = ContextVar("counter", default=5)

    async def tick():
        value = counter.get()
        counter.set(value - 1)
        if value <= 0:
            return FAILURE
        if value == 3:
            raise RuntimeError("3")
        return SUCCESS

    assert run(repeat_until(condition=tick, child=a_func)) == "a"
