# Migration Guide: asyncio → anyio (3.0.0)

async-btree 3.0.0 replaces `asyncio.Runner` with anyio as the sole execution backend.
If you were already using the asyncio path (no curio), this guide covers what changed.

## Dependency changes

Remove:

```toml
pytest-asyncio
```

Add (for non-asyncio backends, optional):

```toml
trio >= 0.26
uvloop >= 0.21
```

## API changes

### BTreeRunner

`BTreeRunner.__init__` now takes `backend` instead of `disable_curio`:

```python
# before
with BTreeRunner() as runner:
    runner.run(my_tree)  # callable — unchanged

# after
with BTreeRunner() as runner:  # asyncio default — no change needed
    runner.run(my_tree)

# new: explicit backend selection
with BTreeRunner(backend="trio") as runner:
    runner.run(my_tree)

with BTreeRunner(backend="asyncio+uvloop") as runner:
    runner.run(my_tree)
```

`runner.run(target, *args, **kwargs)` signature is **unchanged** — callable in both 2.x and 3.0.0.

### run()

Old signature: `run(kernel, target, *args)` — curio-only, deprecated.
New signature: `run(target, *args, backend="asyncio", **kwargs)`.

```python
# before — deprecated, asyncio path via asyncio.Runner directly
import asyncio

asyncio.run(my_tree())

# after — use bt.run()
from async_btree import run

run(my_tree)
run(my_tree, backend="asyncio+uvloop")
```

### parallele — success_threshold typo fixed

The parameter was previously `succes_threshold` (one 's'). It is now `success_threshold`.

```python
# before
parallele(children=[a, b], succes_threshold=1)

# after
parallele(children=[a, b], success_threshold=1)
```

### sequence — success_threshold typo fixed

Same typo fix applies to `sequence`:

```python
# before
sequence(children=[a, b, c], succes_threshold=2)

# after
sequence(children=[a, b, c], success_threshold=2)
```

The property shown in `stringify_analyze` output changes from `succes_threshold: N` to
`success_threshold: N`.

### ControlFlowException.instanciate → instantiate

The method was renamed to fix a typo:

```python
# before
ControlFlowException.instanciate(e)

# after
ControlFlowException.instantiate(e)
```

Behavior is unchanged — pure rename.

### repeat_until semantics corrected — repeat_while added

The old `repeat_until` looped **while condition was truthy**, which is the opposite of
standard BT semantics. 3.0.0 corrects this:

| Function | Loops while condition is... |
|---|---|
| `repeat_while(condition, child)` | truthy (replaces old `repeat_until` behavior) |
| `repeat_until(condition, child)` | falsy (standard BT semantics — stops when condition fires) |

```python
# before — looped while condition was truthy
repeat_until(condition=my_condition, child=my_child)

# after — same behavior, correct name
repeat_while(condition=my_condition, child=my_child)

# new repeat_until — loops until condition becomes truthy
repeat_until(condition=my_condition, child=my_child)
```

### ContextVar isolation — behaviour unchanged

Asyncio users already had isolation via `copy_context()` in `BTreeRunner.__enter__`.
Behaviour is the same in 3.0.0: mutations inside a run do not escape to the caller.

The one difference: with the old `asyncio.Runner` persistent loop, successive `runner.run()`
calls shared ContextVar state. With anyio, each call is isolated from the base snapshot.

```python
# before — mutations accumulated across ticks (asyncio.Runner persistent loop)
with BTreeRunner() as runner:
    runner.run(set_var_to_42)
    runner.run(read_var)  # would see 42

# after — each tick starts from the __enter__ snapshot
with BTreeRunner() as runner:
    runner.run(set_var_to_42)
    runner.run(read_var)  # sees original value, not 42
```

If your code relied on cross-tick ContextVar accumulation, pass state explicitly
via function arguments or use a mutable object (list, dict) set before `__enter__`.

See [tutorial_3_context.py](https://raw.githubusercontent.com/geronimo-iia/async-btree/main/examples/tutorial_3_context.py) for details.

## pytest migration

Replace `pytest-asyncio` with `pytest-anyio` (bundled with anyio):

```python
# before
import pytest

pytestmark = pytest.mark.asyncio


async def test_something(): ...


# after
import pytest

pytestmark = pytest.mark.anyio


async def test_something(): ...
```

Remove `asyncio_mode = "auto"` from `pyproject.toml` if present — anyio does not use it.

Parametrize over backends (optional, recommended):

```python
@pytest.fixture(params=["asyncio", "trio", "asyncio+uvloop"])
def anyio_backend(request):
    backend = request.param
    if backend == "asyncio+uvloop":
        return "asyncio", {"use_uvloop": True}
    return backend, {}
```
