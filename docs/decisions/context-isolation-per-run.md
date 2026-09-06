---
title: "Context Isolation per BTreeRunner.run()"
summary: "Why each run() call executes in an isolated copy_context() snapshot."
status: accepted
last_updated: "2026-09-06"
---

# Context Isolation per BTreeRunner.run()

See also: [Invariants](../invariants.md)

## Decision

`BTreeRunner.__enter__()` captures the caller's `ContextVar` state with `copy_context()`. Each `run()` call executes the target inside an isolated copy of that snapshot. Mutations inside a run do not propagate back to the caller and do not accumulate across ticks.

## Context

Behavior trees are tick-based: `BTreeRunner.run()` is called repeatedly, once per tick. A naive implementation using a persistent event loop (the original asyncio-based design) allowed `ContextVar` mutations inside one tick to survive into the next. This meant tick N's side effects silently affected tick N+1, making tree behavior non-deterministic and hard to test.

## Why Isolated Copies

**Ticks are independent.** Each tick evaluates the tree from the same baseline state. Nodes that set `ContextVar` values communicate within a tick but not across ticks — matching standard BT semantics where each evaluation is a fresh read of the world.

**Deterministic testing.** A test can set up context state once and run multiple ticks without worrying about state leakage between calls. The `xfail` test `test_runner_context_shared_across_runs` documents the intentional non-sharing as a known tradeoff.

**`copy_context()` is cheap.** The copy is shallow — only the mapping of `ContextVar` → value is copied, not the values themselves. For typical usage (a handful of context vars) the overhead is negligible.

## Trade-offs

- Nodes cannot use `ContextVar` to accumulate state across ticks — they must use external mutable state (a class attribute, a closure variable, a database)
- The snapshot is taken at `__enter__`, not at each `run()` call — mutations made between `__enter__` and the first `run()` are included in the baseline
