# Async Behaviour Tree for Python

[![PyPI Version](https://img.shields.io/pypi/v/async-btree.svg)](https://pypi.org/project/async-btree)
[![PyPI License](https://img.shields.io/pypi/l/async-btree.svg)](https://pypi.org/project/async-btree)

Versions following [Semantic Versioning](https://semver.org/)

Requires Python 3.11+. For Python 3.9/3.10 support use [1.x releases](https://github.com/geronimo-iia/async-btree/tree/main-1.x).

See [documentation](https://geronimo-iia.github.io/async-btree).


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

You could build expression like this:

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
This expression apply ```b_decorator``` on function ```a_func```. 
Note that ```decorate(a_func, b_decorator)``` is not an async function, only action, or condition are async function.


Few guidelines of this implementation:

- In order to mimic all NodeStatus (success, failure, running), I replace this by truthy/falsy meaning of evaluation value.
  A special dedicated exception decorate standard exception in order to give them a Falsy meaning (`ControlFlowException`).
  By default, exception are raised like happen usually until you catch them or
  decorate your function with `ignore_exception`.
- Blackboard pattern, act as a manager of context variable for behavior tree.
  With python 3, please... simply use [contextvars](https://docs.python.org/3/library/contextvars.html) !
- In order to be able to build a semantic tree, I've introduce a metadata tuple added on function implementation.

The rest is just implementation details..



A little note:

> You should not use this until you're ready to think about what you're doing :)


### Note about 'async' framework

As we use async function as underlaying mechanism to manage the execution flow, the standard library asyncio is pretty fine.
But, (always a but somewhere isn't it...), you should read this [amazing blog post](https://vorpus.org/blog/some-thoughts-on-asynchronous-api-design-in-a-post-asyncawait-world/) by Nathaniel J. Smith.
And next study [curio](https://github.com/dabeaz/curio) framework in deep.

As curio say:
> Don't Use Curio if You're Allergic to Curio

Personaly, after few time of testing and reading curio code, I'm pretty addict.

If `curio` is not present, we default to `asyncio`.

## Installation

Install with pip or [uv](https://docs.astral.sh/uv/):

 - `pip install async-btree` or `uv add async-btree`
 - with curio extension: `pip install async-btree[curio]` or `uv add async-btree[curio]`


## Usage

See [API Reference documentation](https://geronimo-iia.github.io/async-btree).

Examples:

- [tutorial_1.py](https://github.com/geronimo-iia/async-btree/blob/main/examples/tutorial_1.py) — basic actions, decorators, sequences
- [tutorial_2_decisions.py](https://github.com/geronimo-iia/async-btree/blob/main/examples/tutorial_2_decisions.py) — decision trees and selectors


With this framework, you didn't find any configuration file, no Xml, no json, no yaml.

The main reason (oriented and personal point of view) is that you did not need to introduce an extra level of abstraction 
to declare a composition of functions. I think it's true for most of main use case (except using an editor to wrote behaviour tree for example).

So "If you wrote your function with python, wrote composition in python"... 
_(remember that you did not need XML to do SQL, just write good sql...)_


So, the goal is to:
 - define your business function which implements actions or conditions, with all test case that you wish/need
 - compose them using those provided by this framework like ```sequence```, ```selector```, ...
 - use them as it is or create a well define python module to reuse them


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
