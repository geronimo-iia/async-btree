---
title: "List-Wrapping in sequence() and fallback()"
summary: "Why success returns list[results] rather than a bare scalar."
status: accepted
last_updated: "2026-09-06"
---

# List-Wrapping in sequence() and fallback()

See also: [Invariants](../invariants.md) · [Concepts](../concepts.md)

## Decision

`sequence()` returns `list[results]` on success — all child results collected up to the threshold. `fallback()` and `selector()` return `[result]` — a single-element list wrapping the first truthy result. On failure, both return the last falsy scalar result directly.

## Context

A behavior tree node must return a truthy value on success and a falsy value on failure. For composite nodes that aggregate multiple children, returning a bare scalar on success loses information about which children ran and what they returned.

## Why List-Wrapping

**The return value is always truthy on success.** An empty list `[]` is falsy in Python — returning a list guarantees that a non-empty result list is truthy without any special casing. `sequence` with one successful child returns `[result]`; with three, `[r1, r2, r3]`.

**All child results are preserved.** Callers that need to inspect what happened (logging, debugging, conditional branching on results) have the full picture.

**`success_threshold` generalizes sequence and fallback.** With `success_threshold=len(children)`, all children must succeed (classical sequence). With `success_threshold=1`, the first success wins (fallback). The list return covers both: it always contains exactly the results collected up to the threshold.

## Trade-offs

- Callers that only need a boolean must test `bool(result)` or `if result:` — the list is truthy, not `True`
- Callers that expect a single value must unwrap: `result[0]` for fallback, `result[-1]` for the last sequence element
- Failure returns a bare scalar (the last falsy result), so success and failure have different types — callers must check truthiness before indexing
