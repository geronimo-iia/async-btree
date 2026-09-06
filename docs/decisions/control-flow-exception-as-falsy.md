---
title: "ControlFlowException as Falsy Wrapper"
summary: "Why exceptions are wrapped in a falsy object rather than propagated or converted to False."
status: accepted
last_updated: "2026-09-06"
---

# ControlFlowException as Falsy Wrapper

See also: [Invariants](../invariants.md) · [Concepts](../concepts.md)

## Decision

`action()` catches all exceptions from its target and wraps them in `ControlFlowException`, whose `__bool__()` returns `False`. The exception is stored in `.exception` and never re-raised at the node boundary.

## Context

A behavior tree node can fail in two ways: expected failure (a condition evaluated false) and unexpected failure (an exception). Both must produce a falsy value so composite nodes (`sequence`, `fallback`) can treat them uniformly with `if result:`.

Three alternatives exist:

1. Re-raise exceptions — composite nodes must `try/except` on every child call; error handling leaks into tree logic
2. Return `False` on exception — original cause is lost, debugging impossible
3. Wrap in a falsy exception object — falsy like `False`, but carries the original cause

## Why This Approach

**Composite nodes stay clean.** `sequence`, `fallback`, and `parallele` test `if result:` with no try/except. They do not need to distinguish exception-failure from condition-failure.

**The cause is never lost.** `.exception` holds the original exception. Callers that care about the cause can inspect it; callers that don't can ignore it.

**`ControlFlowException.instantiate()` prevents double-wrapping.** A `ControlFlowException` passed to `instantiate()` is returned unchanged, so wrapping at multiple levels is safe.

## Trade-offs

- Callers that re-raise must unwrap: `raise e.exception` not `raise e`
- An unhandled `ControlFlowException` at the top level is falsy — it will not trigger `except Exception` handlers that test truthiness, though it will be caught by `except Exception` normally
