---
title: "do_while vs repeat_while Semantics"
summary: "Why the library provides two separate loop primitives with explicit at-least-once vs zero-iteration contracts."
status: accepted
last_updated: "2026-09-06"
---

# do_while vs repeat_while Semantics

See also: [Invariants](../invariants.md) · [Concepts](../concepts.md)

## Decision

`do_while(condition, child)` always executes `child` at least once, then checks `condition`. `repeat_while(condition, child)` checks `condition` first and returns `FAILURE` immediately if it is falsy. Both are distinct, named primitives — not a single loop with a `check_first` flag.

## Context

Standard behavior trees define a "repeat" node that loops a child while a condition holds. The ambiguity is whether the condition is checked before or after the first execution. Different BT frameworks resolve this differently; some expose a single node with a mode parameter.

## Why Two Primitives

**Explicit names eliminate ambiguity at the call site.** `do_while(battery_ok, charge)` is unambiguous — `charge` always runs once. `repeat_while(battery_ok, charge)` is unambiguous — `charge` may never run. A `check_first=True/False` parameter forces the reader to track an extra boolean.

**Zero-iteration semantics matter for correctness.** A `repeat_while` that returns `FAILURE` immediately when condition is false on the first check is the correct BT semantics for "guard before looping." A `do_while` that always runs once is the correct semantics for "execute then re-evaluate." Merging them into one node would require a runtime branch invisible in the tree structure.

**`repeat_until` completes the set.** `repeat_until(condition, child)` loops while condition is falsy and succeeds when it becomes truthy — the complement of `repeat_while`. Having all three (`repeat_while`, `repeat_until`, `do_while`) covers every standard loop pattern without ambiguity.

## Trade-offs

- Three loop nodes instead of one — slightly larger API surface
- Callers migrating from frameworks with a single loop node must choose explicitly (the migration guides cover this)
