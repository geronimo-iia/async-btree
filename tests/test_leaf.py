import pytest

from async_btree import action, condition


@pytest.mark.curio
async def test_condition():
    async def target_test(value):
        return value

    assert await condition(target_test, value=True)()  # pylint: disable=unexpected-keyword-arg

    assert not await condition(target_test, value=False)()  # pylint: disable=unexpected-keyword-arg


@pytest.mark.curio
async def test_action_with_exception_is_falsy():
    async def generate_exception():
        raise Exception("Bing!")

    assert not await action(generate_exception)()


@pytest.mark.curio
async def test_action_results():
    async def compute(a, b):
        return a + b

    assert await action(compute, a=1, b=1)() == 2
