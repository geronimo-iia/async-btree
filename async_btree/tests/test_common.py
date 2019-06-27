from libellule.control_flow.common import (
    ControlFlowException,
    SUCCESS,
    FAILURE,
    amap,
    afilter,
)
from curio import run


def test_truthy():
    assert SUCCESS
    assert Exception()
    assert [1, 2]


def test_falsy():
    assert not []
    assert not bool([])
    assert not FAILURE
    assert not bool(FAILURE)
    assert not bool(ControlFlowException(Exception()))


def test_amap():
    async def inc(a):
        return a + 1

    async def process():
        return [i async for i in amap(inc, [1, 2])]

    assert run(process) == [2, 3]


def test_afilter():
    async def even(a):
        return a % 2 == 0

    async def process():
        return [i async for i in afilter(even, [0, 1, 2, 3, 4])]

    assert run(process) == [0, 2, 4]


def test_afilter_amap_aiter():
    async def inc(a):
        return a + 1

    async def even(a):
        return a % 2 == 0

    async def process1():
        return [i async for i in afilter(even, amap(inc, [0, 1, 2, 3, 4]))]

    async def process2():
        return [i async for i in amap(inc, afilter(even, [0, 1, 2, 3, 4]))]

    assert run(process1) == [2, 4]
    assert run(process2) == [1, 3, 5]
