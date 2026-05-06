# How to create a BehaviorTree


In this tutorial series, most of the time Actions will just print some information on console, but keep in mind that real "production" code would probably do something more complicated.


The source code of this tutorial is [example/tutorial_1.py](https://raw.githubusercontent.com/geronimo-iia/async-btree/main/examples/tutorial_1.py).


## How to create your own Action

First, you have to wrote your function (async or sync) as normal, like this:

```python
def approach_object(name: str):
    print(f"approach_object: {name}")

def check_battery():
    print("battery ok")

async def say_hello(name: str):
    print(f"Hello: {name}")

```

At this point, this is not (yet) a behavior action. To define an action, you have to use ```action``` function:

```python
import async_btree as bt

approach_house_object_action = bt.action(target=approach_object, name="house")

check_battery_action = bt.action(target=check_battery)

say_hello_john = bt.action(target=say_hello, name="John")

```


With a class like this one:

```python
class GripperInterface:

    def __init__():
        self._open = False
    

    def open(self):
        print("GripperInterface Open")
        self._open = True
    
    def close(self):
        print("GripperInterface Close")
        self._open = False

```
We can define action for these functions:
    - GripperInterface.open
    - GripperInterface.close


## Create a tree dynamically

We will build a sequence of actions like this one:
 - say hello
 - check battery
 - open gripper
 - approach object
 - close gripper

To do that, we need to use ```sequence``` methods.

```python

gripper = GripperInterface()

b_tree = bt.sequence(children= [
    bt.action(target=say_hello, name="John"),
    bt.action(target=check_battery),
    bt.action(target=gripper.open),
    bt.action(target=approach_object, name="house"),
    bt.action(target=gripper.close)
])

```

Run it — simplest form:

```python
bt.run(b_tree)
```

Or with an explicit backend:

```python
bt.run(b_tree, backend="trio")
bt.run(b_tree, backend="asyncio+uvloop")
```

When you need to run the same tree multiple times in the same context, use `BTreeRunner`:

```python
with bt.BTreeRunner() as runner:
    runner.run(b_tree)
```

And you should see:

```text
Hello: John
```

Why we did not see other action ? It's because our first action did not return a success (something truthy).
So we could add a ```return True```, on each our function, like this:

```python
def approach_object(name: str):
    print(f"approach_object: {name}")
    return True
```

Or we could rewrote our behavior tree with specific status:


```python
b_tree = bt.sequence(children= [
    bt.always_success(child=bt.action(target=say_hello, name="John")),
    bt.always_success(child=bt.action(target=check_battery)),
    bt.always_success(child=bt.action(target=gripper.open)),
    bt.always_success(child=bt.action(target=approach_object, name="house")),
    bt.always_success(child=bt.action(target=gripper.close))
])
```
If we running it again:

```text
Hello: John
battery ok
GripperInterface Open
approach_object: house
GripperInterface Close
```

As you could see:
- we use a single instance of GripperInterface
- we have hard coded name on our action function

We can also define a function like this:

```python
def check_again_battery():
    print("battery dbl check")
    # you should return a success
    return bt.SUCCESS
```

and wrote our behavior tree :

```python
b_tree = bt.sequence(
    children=[
        bt.always_success(child=bt.action(target=say_hello, name="John")),
        bt.action(target=check_battery),
        check_again_battery,  # this will be encapsulated at runtime
        bt.always_success(child=bt.action(target=gripper.open)),
        bt.always_success(child=bt.action(target=approach_object, name="house")),
        bt.always_success(child=bt.action(target=gripper.close)),
    ]
)
```

`check_again_battery` will be encapsulated at runtime.

If we running it again:

```text
Hello: John
battery ok
battery dbl check
GripperInterface Open
approach_object: house
GripperInterface Close
```


In a real use case, we should find a way to avoid this:
- wrote a factory function for a specific case
- either by using ContextVar (```from contextvars import ContextVar```)

You could see a sample in this source is [example/tutorial_2_decisions.py](https://raw.githubusercontent.com/geronimo-iia/async-btree/main/examples/tutorial_2_decisions.py).

## Running trees — bt.run() vs BTreeRunner

`bt.run()` is the simplest entry point: one call, one result, asyncio by default.

```python
result = bt.run(b_tree)
result = bt.run(b_tree, backend="trio")
result = bt.run(b_tree, backend="asyncio+uvloop")
```

Use `BTreeRunner` when you need to run the same tree — or multiple trees — several times from synchronous code, all sharing the same base context snapshot:

```python
with bt.BTreeRunner(backend="asyncio") as runner:
    result1 = runner.run(tree_tick)
    result2 = runner.run(tree_tick)
    result3 = runner.run(tree_tick)
```

The context is captured once at `__enter__` (snapshot of the caller's `ContextVar` state). Each `runner.run()` call starts from that same snapshot — mutations inside a tick do not carry over to the next tick. See [example/tutorial_3_context.py](https://raw.githubusercontent.com/geronimo-iia/async-btree/main/examples/tutorial_3_context.py) for a detailed walkthrough.

For more advanced topics:

- **ContextVar isolation and propagation** — how to pass data into a tree, why mutations don't escape, and how `BTreeRunner` keeps a stable base context across ticks: [example/tutorial_3_context.py](https://raw.githubusercontent.com/geronimo-iia/async-btree/main/examples/tutorial_3_context.py)

- **Exception handling** — `ControlFlowException`, `@ignore_exception`, exception propagation through `parallele` task groups: [example/tutorial_4_exceptions.py](https://raw.githubusercontent.com/geronimo-iia/async-btree/main/examples/tutorial_4_exceptions.py)

- **Routing with switch** — dispatch to different subtrees based on a runtime key; handle unknown cases with a default branch: [example/tutorial_5_switch.py](https://raw.githubusercontent.com/geronimo-iia/async-btree/main/examples/tutorial_5_switch.py)

## Routing with switch

`switch` evaluates a condition to get a key, looks it up in a `cases` dict, and runs the matching child. If no case matches, it runs the `default` child (if provided) or returns `FAILURE`.

```python
from contextvars import ContextVar
import async_btree as bt

mode: ContextVar[str] = ContextVar("mode", default="idle")

async def get_mode() -> str:
    return mode.get()

async def handle_idle() -> bool:
    print("Robot is idle.")
    return bt.SUCCESS

async def handle_patrol() -> bool:
    print("Robot is patrolling.")
    return bt.SUCCESS

async def unknown_mode() -> bool:
    print(f"Unknown mode: {mode.get()!r}")
    return bt.FAILURE

router = bt.switch(
    condition=get_mode,
    cases={
        "idle": handle_idle,
        "patrol": handle_patrol,
    },
    default=unknown_mode,
)
```

The tree representation shows the known case keys and the default branch:

```text
 --> switch:
     case_keys: ['idle', 'patrol']
     --(default)--> unknown_mode:
```

Because `bt.run()` captures the current `ContextVar` state at call time, set the mode before each call:

```python
for m in ["idle", "patrol", "recharge"]:
    mode.set(m)
    bt.run(router)
```

```text
Robot is idle.
Robot is patrolling.
Unknown mode: 'recharge'
```

See [example/tutorial_5_switch.py](https://raw.githubusercontent.com/geronimo-iia/async-btree/main/examples/tutorial_5_switch.py) for the full example.