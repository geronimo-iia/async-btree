import pytest
from curio import sleep

from async_btree import FAILURE, parallele


async def a_func():
    await sleep(1)
    return 'a'


async def b_func():
    await sleep(3)
    return 'b'


async def failure_func():
    await sleep(2)
    return FAILURE


def test_parallele(kernel):
    assert kernel.run(parallele(children=[a_func]))
    assert kernel.run(parallele(children=[a_func, b_func]))
    assert not kernel.run(parallele(children=[a_func, b_func, failure_func]))
    assert kernel.run(parallele(children=[a_func, b_func, failure_func], succes_threshold=2))
    # negative
    with pytest.raises(AssertionError):
        parallele(children=[a_func, b_func, failure_func], succes_threshold=-2)
    # upper than len children
    with pytest.raises(AssertionError):
        parallele(children=[a_func, b_func, failure_func], succes_threshold=4)
