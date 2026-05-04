import pytest

curio = pytest.importorskip("curio")
sleep = curio.sleep

from async_btree import FAILURE, parallele


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
