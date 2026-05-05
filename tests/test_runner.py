import pytest
from contextvars import ContextVar
from async_btree import BTreeRunner, SUCCESS


pytestmark = pytest.mark.anyio


@pytest.fixture(
    params=["asyncio", "trio", "asyncio+uvloop"],
)
def anyio_backend(request):
    backend = request.param
    if backend == "asyncio+uvloop":
        return "asyncio", {"use_uvloop": True}
    return backend, {}


def test_runner_context_manager_default_backend():
    async def _tree() -> bool:
        return SUCCESS

    with BTreeRunner() as runner:
        result = runner.run(_tree)
    assert result == SUCCESS


def test_runner_asyncio_explicit():
    async def _tree() -> bool:
        return SUCCESS

    with BTreeRunner(backend="asyncio") as runner:
        result = runner.run(_tree)
    assert result == SUCCESS


def test_runner_trio():
    async def _tree() -> bool:
        return SUCCESS

    with BTreeRunner(backend="trio") as runner:
        result = runner.run(_tree)
    assert result == SUCCESS


def test_runner_asyncio_uvloop():
    async def _tree() -> bool:
        return SUCCESS

    with BTreeRunner(backend="asyncio+uvloop") as runner:
        result = runner.run(_tree)
    assert result == SUCCESS


def test_runner_context_var_propagation():
    var: ContextVar[str] = ContextVar("var", default="initial")

    async def _tree() -> str:
        return var.get()

    var.set("outer")
    with BTreeRunner() as runner:
        result = runner.run(_tree)
    assert result == "outer"


def test_runner_multiple_runs():
    results = []

    async def _tree(value: int) -> int:
        return value

    with BTreeRunner() as runner:
        results.append(runner.run(_tree, 1))
        results.append(runner.run(_tree, 2))
    assert results == [1, 2]


def test_runner_context_isolation():
    # Gap 3: each BTreeRunner gets fresh copy of outer context, mutations don't escape
    var: ContextVar[int] = ContextVar("var", default=0)

    async def _mutate() -> int:
        var.set(99)
        return var.get()

    var.set(1)
    with BTreeRunner() as runner:
        result = runner.run(_mutate)
    assert result == 99
    assert var.get() == 1  # mutation did not escape to caller


def test_runner_context_shared_across_runs():
    # Gap 3: multiple runner.run() calls within same BTreeRunner share context
    var: ContextVar[int] = ContextVar("var", default=0)

    async def _set(value: int) -> None:
        var.set(value)

    async def _get() -> int:
        return var.get()

    with BTreeRunner() as runner:
        runner.run(_set, 42)
        result = runner.run(_get)
    assert result == 42
