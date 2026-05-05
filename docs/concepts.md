# async-btree: Key Points

## What's a behavior tree?

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


## Why another library?

__SIMPLICITY__

When you study behavior tree implementations — reactive nodes, dynamic changes, runtime execution — at some point you're building something that mimics an `eval/apply` evaluator or a compiler, with a complex hierarchical set of classes.

All the complexity comes from internal state management: trees of blackboards to avoid global variables, multithreading issues, callbacks...

This breaks the simplicity and beauty of the initial design.

What's actually useful about behavior trees:

- clarity of expression
- node tree representation
- possibility to reuse behavior
- external measures to dynamically change behavior — a first step toward observable patterns

Having used OOP for years (very long time), I prefer the power of functional programming: add metadata on a semantic construction, deal with closures, use functions as parameters or return values.

And a last reason, more personal: explore Python expressivity.

## So how?

This module uses coroutines and their mechanisms to manage the execution flow.

By this way:

- we reuse simple language idioms to manage state, parameters, etc.
- no design constraint on action implementation
- most language building blocks can be reused

You can build expressions like this:

```python
async def a_func():
    """A great function"""
    return "a"

async def b_decorator(child_value, other=""):
    """A great decorator..."""
    return f"b{child_value}{other}"

with BTreeRunner() as runner:
    assert runner.run(decorate(a_func, b_decorator)) == "ba"
```

Note that `decorate(a_func, b_decorator)` is not an async function — only actions and conditions are async functions.

## Key design decisions

**Status via truthy/falsy.** To mimic `NodeStatus` (success, failure, running), return values carry truthy/falsy meaning. `ControlFlowException` wraps standard exceptions to give them a falsy meaning. By default, exceptions are raised normally until you catch them or decorate with `ignore_exception`.

**Blackboard pattern?** With Python 3, please... simply use [contextvars](https://docs.python.org/3/library/contextvars.html).

**Abstract tree.** Functions from async-btree build an abstract tree for you. The `node_metadata` decorator adds basic information: function name, parameters, and children relationships. This tree can be retrieved and stringified with `analyze` and `stringify_analyze`.

```python
my_func = alias(child=repeat_until(child=action(hello), condition=success_until_zero), name="btree_1")
print(stringify_analyze(analyze(my_func)))
```

```text
 --> btree_1:
     --(child)--> repeat_until:
         --(condition)--> success_until_zero:
         --(child)--> action:
                      target: hello
```

**No configuration files.** No XML, no JSON, no YAML. You don't need an extra level of abstraction to declare a composition of functions. If you write your functions in Python, write compositions in Python.
_(Remember that you don't need XML to do SQL — just write good SQL...)_


## Core primitives

| Primitive | Role |
|---|---|
| `action` / `condition` | Wrap sync or async functions as BT nodes |
| `sequence` | AND — run children in order, stop on failure |
| `selector` | OR — run children in order, stop on success |
| `repeat_until` | Loop child until condition met |
| `decorate` | Apply decorator function to child output |
| `alias` | Name a subtree |
| `ignore_exception` | Turn exceptions into falsy |
| `always_success` / `always_failure` | Force return semantics on no-return functions |

> You should not use this until you're ready to think about what you're doing :)


## Note about 'curio' and 'async' framework

Since I've started this project in 2020, the Python landscape has changed a lot.

We use async functions as the underlying mechanism to manage the execution flow, and the async framework was (and still is) a real concern.
About this topic you should read this [amazing blog post](https://vorpus.org/blog/some-thoughts-on-asynchronous-api-design-in-a-post-asyncawait-world/) by Nathaniel J. Smith.

[David Beazley](https://github.com/dabeaz) worked on the [curio](https://github.com/dabeaz/curio) framework:
_"Curio is a coroutine-based library for concurrent Python systems programming using async/await. It provides standard programming abstractions such as tasks, sockets, files, locks, and queues as well as some advanced features such as support for structured concurrency. It works on Unix and Windows and has zero dependencies. You'll find it to be familiar, small, fast, and fun."_

As curio says:
> Don't Use Curio if You're Allergic to Curio

Personally, after some time testing and reading curio's code, I'm pretty addicted.

The primary goal of Curio was education and exploration related to asynchronous programming in Python.
After ten years, David Beazley decided to abandon the Curio project. No further maintenance is expected.

Even if I'm sad not to have seen this work included in the Python standard library, for the sanity of the current project, we have to change our async backend to anyio.
This framework, actively maintained, gives us support for asyncio, asyncio + uvloop, and trio.
