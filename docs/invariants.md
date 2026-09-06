# Invariants

Rules that hold at all times across the library. Breaking any of these is a bug, not a design choice.

## Return values

**Every node returns a truthy value on success, falsy on failure.**
`SUCCESS = True`, `FAILURE = False`. All composite nodes propagate this contract — never return `None` or raise uncaught exceptions as the signal.

**`ControlFlowException.__bool__()` is always `False`.**
A wrapped exception is always falsy, regardless of what it wraps. Code that tests `if result:` reliably distinguishes success from failure even when exceptions are involved.

**`sequence()` returns a list on success, a falsy scalar on failure.**
The success value is `list[results]`, not a bare result. Callers that expect a single value must unwrap it.

**`fallback()` and `selector()` wrap their success result in a list.**
`[result]` on first success, last falsy result otherwise. Same list-wrapping contract as `sequence`.

**`parallele()` returns a `bool`, not a result list.**
`True` if successes ≥ threshold, `False` if failures ≥ threshold.

**`parallel_race()` returns the first finisher's result, or `FAILURE` if the child list is empty.**

## State

**`BTreeRunner.run()` executes in an isolated context copy.**
`copy_context()` is called at `__enter__`. Each `run()` call gets a fresh copy. Mutations inside a call never propagate back to the caller's context and never accumulate across ticks.

**`ControlFlowException.instantiate()` is idempotent.**
Passing an already-wrapped exception returns it unchanged — no double-wrapping.

## API contracts

**`success_threshold` must be in `[0, len(children)]`.**
Both `sequence()` and `parallele()` assert this. Out-of-range values raise `AssertionError` at call time, not at runtime.

**`BTreeRunner.run()` must be called inside the context manager.**
Calling it outside raises `RuntimeError`. Always use `async with BTreeRunner(...) as runner:`.

**`get_node_metadata()` raises `RuntimeError` if the target has no `__node_metadata`.**
Decorating a function with `@action` or `@condition` attaches the metadata. Calling `get_node_metadata()` on an undecorated callable is an error.

**`action()` wraps all exceptions as `ControlFlowException`.**
No exception escapes a node boundary as a raw exception. The only way a node signals failure-via-exception is through `ControlFlowException`, which is falsy.

## Behavioral guarantees

**`do_while()` always executes the child at least once.**
The condition is checked *after* the first execution. Use `repeat_while()` if zero iterations is a valid outcome.

**`repeat_while()` returns `FAILURE` immediately if the condition is falsy on the first check.**
Zero iterations produce `FAILURE`, not `SUCCESS`.

**`repeat_until()` returns `FAILURE` immediately if the condition is truthy on the first check.**
Zero iterations produce `FAILURE`, not `SUCCESS`.

**`decision()` with no `failure_tree` returns `SUCCESS` when the condition is falsy.**
It does not return `FAILURE`. Omitting `failure_tree` means "do nothing and succeed" on the false branch.

**`parallel_race()` cancels all remaining tasks when the first child finishes.**
Tasks are not left running in the background.
