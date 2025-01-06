import pytest

from async_btree import FAILURE, SUCCESS, decision


async def i_fail():
    return FAILURE


async def some_action():
    print("continue here...")
    return SUCCESS


@pytest.mark.curio
async def test_usage():
    tree = decision(condition=i_fail, success_tree=some_action, failure_tree=lambda: 42)

    assert await tree() == 42
