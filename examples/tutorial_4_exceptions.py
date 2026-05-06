"""Tutorial 4 - Exception handling in behavior trees

By default, any exception raised inside a node propagates up and crashes the tree.
async-btree provides two tools to handle this:

  1. @ignore_exception  — decorator that catches exceptions and returns FAILURE
                          so the tree keeps running instead of crashing.

  2. ControlFlowException — wrapper raised when an unhandled exception escapes
                            a node group (e.g. parallele task group). It carries
                            the original exception and is itself falsy.

"""

import async_btree as bt

# ── Example 1: unhandled exception crashes the tree ───────────────────────

print("=== Example 1: raw exception propagates ===")


async def unreliable_sensor() -> bool:
    raise OSError("sensor disconnected")


try:
    bt.run(bt.action(target=unreliable_sensor))
except bt.ControlFlowException as e:
    print(f"  caught ControlFlowException, original cause: {e.__cause__!r}")


# ── Example 2: @ignore_exception turns exception into FAILURE ──────────────

print("\n=== Example 2: @ignore_exception → FAILURE ===")


@bt.ignore_exception
async def safe_sensor() -> bool:
    raise OSError("sensor disconnected")


async def fallback_reading() -> bool:
    print("  using fallback reading")
    return bt.SUCCESS


# fallback: try safe_sensor first, use fallback_reading if it fails.
# fallback succeeds if at least one child succeeds (success_threshold=1).
tree = bt.fallback(children=[bt.action(target=safe_sensor), bt.action(target=fallback_reading)])
result = bt.run(tree)
# result is a list of child outcomes; tree succeeded because one child did
print(f"  tree result = {result!r}, any success = {any(bool(r) for r in result)}")


# ignore_exception can also be applied at tree-construction time instead of
# at function-definition time. Use this when you don't own the function
# (third-party code, generated callables, or wrapping conditionally).
#
# "by design" with @ignore_exception means fault-tolerance is part of the node
# contract — the function is always safe to call. Use the call form when the
# decision is external to the node (e.g. building resilient subtrees from
# functions that may or may not raise).
async def raw_sensor() -> bool:
    raise OSError("sensor disconnected")


# applied at construction time — fault-tolerance decided by the tree builder
safe_by_design = bt.ignore_exception(raw_sensor)

# useful when building trees dynamically from a list of untrusted callables
nodes = [raw_sensor]
safe_nodes = [bt.ignore_exception(n) for n in nodes]

tree2 = bt.fallback(children=[bt.action(target=safe_by_design), bt.action(target=fallback_reading)])
result2 = bt.run(tree2)
print(f"  dynamic wrap result = {result2!r}, any success = {any(bool(r) for r in result2)}")


# ── Example 3: ControlFlowException from parallele ────────────────────────

print("\n=== Example 3: undecorated exception in parallele → ControlFlowException ===")


async def bad_node() -> bool:
    raise RuntimeError("hardware failure")


async def good_node() -> bool:
    print("  good_node ran")
    return bt.SUCCESS


parallel_tree = bt.parallele(children=[bad_node, good_node], success_threshold=2)

try:
    bt.run(parallel_tree)
except bt.ControlFlowException as e:
    print(f"  caught ControlFlowException, original cause: {e.__cause__!r}")


# ── Example 4: @ignore_exception in parallele counts as FAILURE ───────────

print("\n=== Example 4: @ignore_exception in parallele → counts as FAILURE ===")


@bt.ignore_exception
async def safe_bad_node() -> bool:
    raise RuntimeError("hardware failure")


parallel_tree_safe = bt.parallele(children=[safe_bad_node, good_node], success_threshold=2)
result = bt.run(parallel_tree_safe)
print(f"  tree result with threshold=2, one failure = {result}")  # FAILURE

parallel_tree_safe_low = bt.parallele(children=[safe_bad_node, good_node], success_threshold=1)
result = bt.run(parallel_tree_safe_low)
print(f"  tree result with threshold=1, one failure = {result}")  # SUCCESS
