---
title: "anyio as Sole Async Backend"
summary: "Why curio was dropped in 3.0 and anyio became the only backend."
status: accepted
last_updated: "2026-09-06"
---

# anyio as Sole Async Backend

See also: [Invariants](../invariants.md) · [Migration: curio → anyio](../migration/curio-to-anyio.md)

## Decision

3.0.0 removed curio support entirely. anyio (`asyncio`, `trio`, `asyncio+uvloop`) is the sole backend. `BTreeRunner(backend=)` replaces the old `BTreeRunner(disable_curio=)` parameter.

## Context

The library originally supported curio as an alternative async backend alongside asyncio. Maintaining curio compatibility required conditional code paths in `BTreeRunner`, separate CI matrix entries, and a `[curio]` optional dependency group.

## Why Drop Curio

**curio is effectively unmaintained.** No releases since 2021. The anyio abstraction covers asyncio and trio — the two backends with active development and ecosystem support.

**Maintaining two backends doubled the test surface.** Conditional code paths in `BTreeRunner`, separate CI matrix entries, and a `[curio]` optional dep group — all for a backend whose user base was small relative to asyncio and trio.

**anyio's `Backend` literal (`"asyncio"`, `"trio"`, `"asyncio+uvloop"`) provides the same flexibility** with a maintained abstraction layer. Switching backends is a one-argument change at `BTreeRunner` construction.

## Trade-offs

- Existing curio users must migrate (migration guide at `docs/migration/curio-to-anyio.md`)
- anyio adds a dependency that was previously optional — now always required
