import pytest

from async_btree import ControlFlowException, action


@pytest.mark.curio
async def test_action_result_with_exceptions():
    def div_zero():
        return 1 / 0

    fn = action(target=div_zero)
    assert fn
    with pytest.raises(ControlFlowException):
        await fn()
