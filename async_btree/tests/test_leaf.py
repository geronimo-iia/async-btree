from libellule.control_flow.leaf import action, condition
from curio import run


def test_condition():
    async def target_test(value):
        return value

    assert run(
        condition(target_test, value=True)
    )  # pylint: disable=unexpected-keyword-arg

    assert not run(
        condition(target_test, value=False)
    )  # pylint: disable=unexpected-keyword-arg


def test_action_with_exception_is_falsy():
    async def generate_exception():
        raise Exception("Bing!")

    assert not run(action(generate_exception))


def test_action_results():
    async def compute(a, b):
        return a + b

    assert run(action(compute, a=1, b=1)) == 2
