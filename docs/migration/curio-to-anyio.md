# Migration Guide: curio → anyio (3.0.0)

async-btree 3.0.0 drops curio entirely. anyio replaces it as the sole async backend.

## Why

curio is no longer maintained at the same pace. anyio provides a stable, backend-agnostic API
that runs on asyncio, trio, and asyncio+uvloop — tested uniformly across all three.

## Dependency changes

Remove:

```toml
# pyproject.toml — remove these
"async-btree[curio]"
curio
pytest-curio
```

Add:

```toml
"async-btree >= 3.0.0"
```

Optional extras for non-asyncio backends:

```toml
# trio backend
trio >= 0.26

# uvloop backend (asyncio only)
uvloop >= 0.21
```

## API changes

### BTreeRunner

`BTreeRunner` no longer accepts `disable_curio`. It now accepts `backend`:

```python
# before
with BTreeRunner() as runner:            # used curio if installed
    runner.run(my_tree)                  # callable + args, unchanged

with BTreeRunner(disable_curio=True) as runner:  # forced asyncio
    runner.run(my_tree)

# after
with BTreeRunner() as runner:            # asyncio by default
    runner.run(my_tree)                  # same callable signature

with BTreeRunner(backend="trio") as runner:
    runner.run(my_tree)

with BTreeRunner(backend="asyncio+uvloop") as runner:
    runner.run(my_tree)
```

`runner.run(target, *args, **kwargs)` signature is **unchanged** — it takes a callable, not a coroutine, in both 2.x and 3.0.0.

### run()

The old `run(kernel, target, *args)` curio helper is gone.
New `run()` is a one-shot convenience wrapper:

```python
# before
import curio
from async_btree import run
run(curio.Kernel(), my_tree)

# after
from async_btree import run
run(my_tree)                          # asyncio default
run(my_tree, backend="trio")
run(my_tree, backend="asyncio+uvloop")
```

### has_curio

Removed entirely. No replacement — the curio detection path no longer exists.

```python
# before
from async_btree.utils import has_curio
if has_curio():
    ...

# after — delete this code
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

### ContextVar isolation

With curio, `BTreeRunner` kept a persistent kernel across `run()` calls.
ContextVar mutations accumulated from tick to tick.

With anyio, each `runner.run()` call is isolated — mutations inside a tick
do not propagate to the next tick. The context is snapshotted once at `__enter__`.

```python
var = ContextVar("x", default=0)
var.set(1)

with BTreeRunner() as runner:
    runner.run(mutate_var)   # sets var to 99 inside
    # var is still 1 here — isolation is intentional

var.get()  # → 1
```

See [tutorial_3_context.py](https://raw.githubusercontent.com/geronimo-iia/async-btree/main/examples/tutorial_3_context.py) for details.

## pytest migration

Replace `pytest-curio` with `pytest-anyio` (bundled with anyio):

```python
# before
@pytest.mark.curio
async def test_something():
    ...

# after
import pytest
pytestmark = pytest.mark.anyio

async def test_something():
    ...
```

Parametrize over backends with the `anyio_backend` fixture:

```python
@pytest.fixture(params=["asyncio", "trio", "asyncio+uvloop"])
def anyio_backend(request):
    backend = request.param
    if backend == "asyncio+uvloop":
        return "asyncio", {"use_uvloop": True}
    return backend, {}
```
