from async_btree import action, condition


def test_condition(kernel):
    async def target_test(value):
        return value

    assert kernel.run(condition(target_test, value=True))  # pylint: disable=unexpected-keyword-arg

    assert not kernel.run(condition(target_test, value=False))  # pylint: disable=unexpected-keyword-arg


def test_action_with_exception_is_falsy(kernel):
    async def generate_exception():
        raise Exception("Bing!")

    assert not kernel.run(action(generate_exception))


def test_action_results(kernel):
    async def compute(a, b):
        return a + b

    assert kernel.run(action(compute, a=1, b=1)) == 2
