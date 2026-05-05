import pytest
from async_btree import ControlFlowException, ignore_exception, parallele, FAILURE, SUCCESS


pytestmark = pytest.mark.anyio


@pytest.fixture(
    params=["asyncio", "trio", "asyncio+uvloop"],
)
def anyio_backend(request):
    backend = request.param
    if backend == "asyncio+uvloop":
        return "asyncio", {"use_uvloop": True}
    return backend, {}


async def test_parallele_all_success():
    async def _success() -> bool:
        return SUCCESS

    result = await parallele(children=[_success, _success])()
    assert result == SUCCESS


async def test_parallele_threshold_met():
    async def _success() -> bool:
        return SUCCESS

    async def _failure() -> bool:
        return FAILURE

    result = await parallele(children=[_success, _failure], success_threshold=1)()
    assert result == SUCCESS


async def test_parallele_threshold_not_met():
    async def _success() -> bool:
        return SUCCESS

    async def _failure() -> bool:
        return FAILURE

    result = await parallele(children=[_success, _failure], success_threshold=2)()
    assert result == FAILURE


async def test_parallele_raw_exception_raises_control_flow():
    async def _raises() -> bool:
        raise ValueError("boom")

    async def _success() -> bool:
        return SUCCESS

    with pytest.raises(ControlFlowException):
        await parallele(children=[_raises, _success], success_threshold=2)()


async def test_parallele_exception_counts_as_failure():
    @ignore_exception
    async def _raises() -> bool:
        raise ValueError("boom")

    async def _success() -> bool:
        return SUCCESS

    result = await parallele(children=[_raises, _success], success_threshold=2)()
    assert result == FAILURE


async def test_parallele_exception_below_threshold_still_passes():
    @ignore_exception
    async def _raises() -> bool:
        raise ValueError("boom")

    async def _success() -> bool:
        return SUCCESS

    result = await parallele(children=[_raises, _success], success_threshold=1)()
    assert result == SUCCESS


async def test_parallele_all_fail():
    async def _failure() -> bool:
        return FAILURE

    result = await parallele(children=[_failure, _failure])()
    assert result == FAILURE


async def test_parallele_metadata():
    # Gap 5: verify success_threshold (correct spelling) in node metadata
    node = parallele(children=[lambda: None], success_threshold=1)
    assert node.__node_metadata.name == "parallele"
    assert "success_threshold" in node.__node_metadata.properties


async def test_parallele_empty():
    # Gap 6: new edge case — no children, threshold 0
    result = await parallele(children=[], success_threshold=0)()
    assert result == SUCCESS
