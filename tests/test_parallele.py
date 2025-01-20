from asyncio import sleep as asyncio_sleep

import pytest
from curio import sleep

from async_btree import FAILURE, parallele
from async_btree.parallele import parallele_asyncio


async def a_func():
    await sleep(1)
    return "a"


async def b_func():
    await sleep(3)
    return "b"


async def failure_func():
    await sleep(2)
    return FAILURE


async def asyncio_a_func():
    await asyncio_sleep(1)
    return "a"


async def asyncio_b_func():
    await asyncio_sleep(3)
    return "b"


async def asyncio_failure_func():
    await asyncio_sleep(2)
    return FAILURE


def c_func():
    return "c"


@pytest.mark.curio
async def test_parallele():
    assert await parallele(children=[a_func])()
    assert await parallele(children=[a_func, b_func])()
    assert not await parallele(children=[a_func, b_func, failure_func])()
    assert await parallele(children=[a_func, b_func, failure_func], succes_threshold=2)()
    # negative
    with pytest.raises(AssertionError):
        parallele(children=[a_func, b_func, failure_func], succes_threshold=-2)
    # upper than len children
    with pytest.raises(AssertionError):
        parallele(children=[a_func, b_func, failure_func], succes_threshold=4)

    meta = parallele(children=[a_func, b_func, failure_func], succes_threshold=2).__node_metadata
    assert meta.name == "parallele"
    assert "succes_threshold" in meta.properties


@pytest.mark.curio
async def test_parallele_with_sync_function():
    assert await parallele(children=[c_func])()
    assert await parallele(children=[a_func, b_func, c_func])()
    assert not await parallele(children=[a_func, b_func, c_func, failure_func])()


@pytest.mark.asyncio
async def test_parallele_asyncio():
    assert await parallele_asyncio(children=[asyncio_a_func], succes_threshold=1)()
    assert await parallele_asyncio(children=[asyncio_a_func, asyncio_b_func], succes_threshold=2)()
    assert not await parallele_asyncio(
        children=[asyncio_a_func, asyncio_b_func, asyncio_failure_func],
        succes_threshold=3,
    )()
    assert await parallele_asyncio(
        children=[asyncio_a_func, asyncio_b_func, asyncio_failure_func],
        succes_threshold=2,
    )()

    meta = parallele_asyncio(
        children=[asyncio_a_func, asyncio_b_func, asyncio_failure_func],
        succes_threshold=2,
    ).__node_metadata
    assert meta.name == "parallele"
    assert "succes_threshold" in meta.properties
