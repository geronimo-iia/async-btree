from asyncio import sleep

import pytest

from async_btree import FAILURE
from async_btree.parallele import parallele_asyncio
from async_btree.utils import to_async


async def a_func():
    await sleep(1)
    return "a"


async def b_func():
    await sleep(3)
    return "b"


async def failure_func():
    await sleep(2)
    return FAILURE


def c_func():
    return "c"


@pytest.mark.asyncio
async def test_parallele_asyncio_basic():
    assert await parallele_asyncio(children=[a_func], succes_threshold=1)()
    assert await parallele_asyncio(children=[a_func, b_func], succes_threshold=2)()
    assert not await parallele_asyncio(children=[a_func, b_func, failure_func], succes_threshold=3)()
    assert await parallele_asyncio(children=[a_func, b_func, failure_func], succes_threshold=2)()


@pytest.mark.asyncio
async def test_parallele_asyncio_metadata():
    meta = parallele_asyncio(
        children=[a_func, b_func, failure_func],
        succes_threshold=2,
    ).__node_metadata
    assert meta.name == "parallele"
    assert "succes_threshold" in meta.properties


@pytest.mark.asyncio
async def test_parallele_asyncio_with_sync_function():
    assert await parallele_asyncio(children=[to_async(c_func)], succes_threshold=1)()
    assert await parallele_asyncio(children=[a_func, b_func, to_async(c_func)], succes_threshold=3)()
    assert not await parallele_asyncio(children=[a_func, b_func, to_async(c_func), failure_func], succes_threshold=4)()


@pytest.mark.asyncio
async def test_parallele_asyncio():
    assert await parallele_asyncio(children=[a_func], succes_threshold=1)()
    assert await parallele_asyncio(children=[a_func, b_func], succes_threshold=2)()
    assert not await parallele_asyncio(
        children=[a_func, b_func, failure_func],
        succes_threshold=3,
    )()
    assert await parallele_asyncio(
        children=[a_func, b_func, failure_func],
        succes_threshold=2,
    )()

    meta = parallele_asyncio(
        children=[a_func, b_func, failure_func],
        succes_threshold=2,
    ).__node_metadata
    assert meta.name == "parallele"
    assert "succes_threshold" in meta.properties
