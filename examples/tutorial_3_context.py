"""Tutorial 3 - ContextVar isolation and propagation

Behavior trees run in an isolated copy of the caller's context.

Key rules:
  1. The caller can pass data IN by setting a ContextVar before run().
  2. Mutations made INSIDE the tree do NOT escape back to the caller.
  3. With BTreeRunner, all run() calls share the same base snapshot
     captured at __enter__ — mutations from one tick do not carry to the next.

"""

import contextvars

import async_btree as bt

sensor_value: contextvars.ContextVar[float] = contextvars.ContextVar("sensor_value", default=0.0)
tick_count: contextvars.ContextVar[int] = contextvars.ContextVar("tick_count", default=0)


async def read_sensor() -> bool:
    print(f"  sensor_value inside tree = {sensor_value.get()}")
    return bt.SUCCESS


async def mutate_sensor() -> bool:
    sensor_value.set(999.0)
    print(f"  sensor_value mutated to {sensor_value.get()} inside tree")
    return bt.SUCCESS


async def increment_tick() -> bool:
    tick_count.set(tick_count.get() + 1)
    print(f"  tick_count inside tree = {tick_count.get()}")
    return bt.SUCCESS


# ── Example 1: caller sets a value, tree reads it ──────────────────────────

print("=== Example 1: pass data IN via ContextVar ===")
sensor_value.set(42.5)
bt.run(read_sensor)
print(f"caller sensor_value after run = {sensor_value.get()}")  # still 42.5


# ── Example 2: mutations inside tree do NOT escape ────────────────────────

print("\n=== Example 2: mutations inside tree are isolated ===")
sensor_value.set(1.0)
bt.run(mutate_sensor)
print(f"caller sensor_value after run = {sensor_value.get()}")  # still 1.0, not 999.0


# ── Example 3: BTreeRunner — each tick starts from the same base snapshot ─

print("\n=== Example 3: BTreeRunner ticks share the same base snapshot ===")
tick_count.set(0)
with bt.BTreeRunner() as runner:
    # Each run() starts from tick_count=0 (captured at __enter__)
    # Mutations inside do not accumulate across ticks.
    for _ in range(3):
        runner.run(increment_tick)

print(f"caller tick_count after 3 ticks = {tick_count.get()}")  # still 0
