from contextvars import ContextVar

import pytest

from async_btree import (
    action,
    alias,
    analyze,
    inverter,
    repeat_until,
    retry,
    sequence,
    stringify_analyze,
)

max_n = ContextVar("max_n", default=5)


async def success_until_zero():
    max_n.set(max_n.get() - 1)
    return max_n.get() >= 0


def hello():  # we could define it as sync or async
    n = max_n.get()
    if n > 0:
        print(f"{n}...")
    else:
        print("BOOM !!")


def test_node_str():
    node = analyze(alias(child=action(target=hello), name="a test"))
    printed_tree = """ --> a test:\n     --(child)--> action:\n                  target: hello\n"""
    assert str(node) == printed_tree


def test_analyze_tree_1():
    tree_1 = alias(
        child=repeat_until(child=action(hello), condition=success_until_zero),
        name="btree_1",
    )

    a_tree_1 = analyze(tree_1)

    printed_tree = """ --> btree_1:\n     --(child)--> repeat_until:\n         --(condition)--> success_until_zero:\n         --(child)--> action:\n                      target: hello\n"""  # noqa: E501, B950

    assert stringify_analyze(a_tree_1) == printed_tree


def test_analyze_tree_2():
    tree_2 = retry(child=inverter(child=action(hello)), max_retry=10)
    a_tree_2 = analyze(tree_2)

    printed_tree = """ --> retry:\n     max_retry: 10\n     --(child)--> inverter:\n         --(child)--> action:\n                      target: hello\n"""  # noqa: E501, B950

    assert stringify_analyze(a_tree_2) == printed_tree


def test_analyze_failure():
    def ugly():
        return True

    ugly.__node_metadata = {}

    with pytest.raises(RuntimeError):
        analyze(ugly)


def test_analyze_simple_function():
    print_test = """ --> hello:\n"""
    assert stringify_analyze(analyze(hello)) == print_test


def test_analyze_sequence():
    a_tree = analyze(
        alias(
            child=repeat_until(
                child=sequence(children=[action(hello), action(hello), action(hello)]),
                condition=success_until_zero,
            ),
            name="btree_1",
        )
    )
    print_test = """ --> btree_1:\n     --(child)--> repeat_until:\n         --(condition)--> success_until_zero:\n         --(child)--> sequence:\n                      succes_threshold: 3\n             --(children)--> action:\n                             target: hello\n             --(children)--> action:\n                             target: hello\n             --(children)--> action:\n                             target: hello\n"""  # noqa: E501, B950
    assert stringify_analyze(a_tree) == print_test
