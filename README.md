# Async Behaviour Tree for Python

[![PyPI Version](https://img.shields.io/pypi/v/async-btree.svg)](https://pypi.org/project/async-btree)
[![PyPI License](https://img.shields.io/pypi/l/async-btree.svg)](https://pypi.org/project/async-btree)

Versions following [Semantic Versioning](https://semver.org/)

See [documentation](https://geronimo-iia.github.io/async-btree).

Requires Python 3.11+. 
For Python 3.9/3.10 support use [1.x releases](https://github.com/geronimo-iia/async-btree/tree/main-1.x).
For 2.x (asyncio/curio) use [2.x releases](https://github.com/geronimo-iia/async-btree/tree/main-2.x).


## Overview


### What's a behavior tree ?

> Unlike a Finite State Machine, a Behaviour Tree is a tree of hierarchical nodes that controls the flow of decision and the execution of "tasks" or, as we will call them further, "Actions".
> -- <cite>[behaviortree](https://www.behaviortree.dev/bt_basics/)</cite>

If you're new (or not) to behavior tree, you could spend some time on this few links:

- [Behavior trees for AI: How they work](https://www.gamasutra.com/blogs/ChrisSimpson/20140717/221339/Behavior_trees_for_AI_How_they_work.php) by Chris Simpson
- [Introduction to BTs](https://www.behaviortree.dev/bt_basics/)

Few implementation libraries:

- [task_behavior_engine](https://github.com/ToyotaResearchInstitute/task_behavior_engine) A behavior tree based task engine written in Python
- [pi_trees](https://github.com/pirobot/pi_trees/) a Python/ROS library for implementing Behavior Trees
- [pr_behavior_tree](https://github.com/personalrobotics/pr_behavior_tree) A simple python behavior tree library based on coroutines
- [btsk](https://github.com/aigamedev/btsk) Behavior Tree Starter Kit
- [behave](https://github.com/fuchen/behave) A behavior tree implementation in Python


### Why another library so ?

__SIMPLICITY__

When you study behavior tree implementation, reactive node, dynamic change, runtime execution, etc ...
At a moment you're build more or less something that mimic an evaluator 'eval/apply' or a compilator, with a complex hierarchical set of class.

All complexity came with internal state management, using tree of blackboard to avoid global variable, multithreading issue, maybe few callback etc ...

This break the simplicity and beauty of your initial design.

What I find useful with behavior tree:

- clarity of expression
- node tree representation
- possibility to reuse behavior
- add external measure to dynamicaly change a behavior, a first step on observable pattern...

As I've used OOP for years (very long time), I will try to avoid class tree and prefer using the power of functional programming to obtain what I want: add metadata on a semantic construction, deal with closure, use function in parameters or in return value...

And a last reason, more personal, it that i would explore python expressivity.

__SO HOW ?__

In this module, I propose using the concept of coroutines, and their mechanisms to manage the execution flow.
By this way:

- we reuse simple language idiom to manage state, parameter, etc
- no design constraint on action implementation
- most of language build block could be reused

To resume:
> This library uses coroutines and functional composition instead. No class trees. No configuration files (no XML, no JSON, no YAML). Business logic is plain Python functions. Composition is plain Python.

The main reason (oriented and personal point of view) is that you did not need to introduce an extra level of abstraction 
to declare a composition of functions. I think it's true for most of main use case (except using an editor to wrote behaviour tree for example).

So "If you wrote your function with python, wrote composition in python"... 
_(remember that you did not need XML to do SQL, just write good sql...)_


You could build expression like this:

```python
import async_btree as bt

async def a_func():
    return "a"

async def b_decorator(child_value, other=""):
    return f"b{child_value}{other}"

assert bt.run(bt.decorate(a_func, b_decorator)) == "ba"
```
This expression apply ```b_decorator``` on function ```a_func```. 
Note that ```decorate(a_func, b_decorator)``` is not an async function, only action, or condition are async function.


Want an abstract tree of our behaviour tree ?

Functions from async-btree build an abstract tree for you. 
If you lookup in code, you should see an annotation "node_metadata" on internal implementation. 
This decorator add basic information like function name, parameters, and children relation ship.

This abstract tree can be retrieved and stringified with ```analyze``` and ```stringify_analyze```.
Here the profile:

```python
  def analyze(target: CallableFunction) -> Node: # here we have our "abstract tree code"
    ...
```

For example:

```python

# your behaviour tree, or a sub tree:
my_func = alias(child=repeat_until(child=action(hello), condition=success_until_zero), name="btree_1")

# retrieve meta information and build a Node tree
abstract_tree_tree_1 = analyze(my_func) 

# output the tree:
print(stringify_analyze(abstract_tree_tree_1))
```

This should print:

```text
 --> btree_1:
     --(child)--> repeat_until:
         --(condition)--> success_until_zero:
         --(child)--> action:
                      target: hello
```


Note about action and condition method:

 - you could use sync or async function
 - you could specify a return value with SUCCESS or FAILURE
 - function with no return value will be evaluated as FAILURE until you decorate them with a `always_success`or `always_failure`

### Key design decisions

- **Truthy/falsy as node status** — `SUCCESS` / `FAILURE` are `True` / `False`. Exceptions are wrapped in `ControlFlowException` to give them falsy meaning without losing the original cause.
- **ContextVar as blackboard** — no custom blackboard class needed. Use Python's built-in [`contextvars`](https://docs.python.org/3/library/contextvars.html).
- **Node metadata** — `@node_metadata` decorates inner functions with name, parameters, and child relationships. This builds the abstract tree used by `analyze()`.

See [Concepts](https://geronimo-iia.github.io/async-btree/concepts/) for a deeper explanation of the design principles.

The rest is just implementation details..


### Async backend

3.0.0 uses [anyio](https://anyio.readthedocs.io/) as the sole backend. Three runtimes supported:

| Backend           | Value              |
| ----------------- | ------------------ |
| asyncio (default) | `"asyncio"`        |
| trio              | `"trio"`           |
| asyncio + uvloop  | `"asyncio+uvloop"` |


## Installation

```bash
pip install async-btree
# or
uv add async-btree
```

Optional extras for non-asyncio backends:

```bash
uv add trio           # trio backend
uv add uvloop         # asyncio+uvloop backend
```

**Migrating from 2.x?** See the [migration guides](https://geronimo-iia.github.io/async-btree/migration/curio-to-anyio/) in the documentation.


## Usage

See [API Reference documentation](https://geronimo-iia.github.io/async-btree).

### One-shot run

```python
import async_btree as bt

result = bt.run(my_tree)                          # asyncio (default)
result = bt.run(my_tree, backend="trio")
result = bt.run(my_tree, backend="asyncio+uvloop")
```

### Multiple runs in the same context

```python
with bt.BTreeRunner(backend="asyncio") as runner:
    result1 = runner.run(tree_tick)
    result2 = runner.run(tree_tick)
```

Each `runner.run()` starts from the context snapshot captured at `__enter__` — ContextVar mutations inside a tick do not carry over to the next tick.

### Building trees

```python
import async_btree as bt

b_tree = bt.sequence(children=[
    bt.always_success(child=bt.action(target=say_hello, name="John")),
    bt.action(target=check_battery),
    bt.always_success(child=bt.action(target=gripper.open)),
    bt.always_success(child=bt.action(target=approach_object, name="house")),
    bt.always_success(child=bt.action(target=gripper.close)),
])

bt.run(b_tree)
```


### Concurrent execution

```python
parallel_tree = bt.parallele(
    children=[sensor_a, sensor_b, sensor_c],
    success_threshold=2,   # succeed if at least 2 children succeed
)
result = bt.run(parallel_tree)
```

### Exception handling

```python
@bt.ignore_exception
async def unreliable_sensor() -> bool:
    raise IOError("disconnected")

# or apply dynamically at tree construction time
safe = bt.ignore_exception(unreliable_sensor)
```

### Tree introspection

```python
my_func = bt.alias(child=bt.repeat_until(child=bt.action(hello), condition=success_until_zero), name="btree_1")

abstract_tree = bt.analyze(my_func)
print(bt.stringify_analyze(abstract_tree))
```

```text
 --> btree_1:
     --(child)--> repeat_until:
         --(condition)--> success_until_zero:
         --(child)--> action:
                      target: hello
```


## Examples

- [tutorial_1.py](https://github.com/geronimo-iia/async-btree/blob/main/examples/tutorial_1.py) — basic actions, decorators, sequences, backend selection
- [tutorial_2_decisions.py](https://github.com/geronimo-iia/async-btree/blob/main/examples/tutorial_2_decisions.py) — decision trees and selectors with ContextVar
- [tutorial_3_context.py](https://github.com/geronimo-iia/async-btree/blob/main/examples/tutorial_3_context.py) — ContextVar isolation and propagation
- [tutorial_4_exceptions.py](https://github.com/geronimo-iia/async-btree/blob/main/examples/tutorial_4_exceptions.py) — exception handling, `ControlFlowException`, `parallele`

See full [API Reference](https://geronimo-iia.github.io/async-btree) and [Tutorial](https://geronimo-iia.github.io/async-btree/tutorial/).
