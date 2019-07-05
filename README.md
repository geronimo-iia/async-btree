# Overview

Async behavior tree for python


[![Unix Build Status](https://img.shields.io/travis/geronimo-iia/async-btree/master.svg?label=unix)](https://travis-ci.org/geronimo-iia/async-btree)
[![Coverage Status](https://img.shields.io/coveralls/geronimo-iia/async-btree/master.svg)](https://coveralls.io/r/geronimo-iia/async-btree)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/fe669a02b4aa46b5b1faf619ba2bf382)](https://www.codacy.com/app/geronimo-iia/async-btree?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=geronimo-iia/async-btree&amp;utm_campaign=Badge_Grade)
[![Scrutinizer Code Quality](https://img.shields.io/scrutinizer/g/geronimo-iia/async-btree.svg)](https://scrutinizer-ci.com/g/geronimo-iia/async-btree/?branch=master)
[![PyPI Version](https://img.shields.io/pypi/v/async-btree.svg)](https://pypi.org/project/async-btree)
[![PyPI License](https://img.shields.io/pypi/l/async-btree.svg)](https://pypi.org/project/async-btree)

Versions following [Semantic Versioning](https://semver.org/)

## What's a behavior tree ?

> Unlike a Finite State Machine, a Behaviour Tree is a tree of hierarchical nodes that controls the flow of decision and the execution of "tasks" or, as we will call them further, "Actions".
> -- <cite>[behaviortree](https://www.behaviortree.dev/bt_basics/)</cite>

If your new (or not) about behavior tree, you could spend some time on this few links:

- [Behavior trees for AI: How they work](https://www.gamasutra.com/blogs/ChrisSimpson/20140717/221339/Behavior_trees_for_AI_How_they_work.php) by Chris Simpson
- [Introduction to BTs](https://www.behaviortree.dev/bt_basics/)

Few implementation libraries:

- [task_behavior_engine](https://github.com/ToyotaResearchInstitute/task_behavior_engine) A behavior tree based task engine written in Python
- [pi_trees](https://github.com/pirobot/pi_trees/) a Python/ROS library for implementing Behavior Trees
- [pr_behavior_tree](https://github.com/personalrobotics/pr_behavior_tree) A simple python behavior tree library based on coroutines
- [btsk](https://github.com/aigamedev/btsk) Behavior Tree Starter Kit
- [behave](https://github.com/fuchen/behave) A behavior tree implementation in Python


## Why another library so ?

When you study behavior tree implementation, reactive node, dynamic change, runtime execution, etc ... 
At a moment you're build more or less something that mimic an evaluator 'eval/apply' or a compilator, with a complex hierachical set of class.
All complexity came with internal state management, using tree of blackboard to avoid global variable, multithreading issue, maybe few callback etc ...
This break the simplicity and beauty of your initial design.

What I find usefull with behavior tree:

- clarity of expression
- node tree representation
- possibility to reuse behavior
- add external measure to dynamicaly change a behavior, a first step on observable pattern...

As I've used OOP for years (very long time), I will try to avoid class tree and prefer using the power of functionnal programming to obtain what I want: add metadata on a sematic construction, deal with closure, use function in parameters or in return value...

And a last reason, more personal, it that i would explore python expressivity.

So, in this module, I purpose you to use the concept of coroutines, and their mecanisms to manage the execution flow.
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

assert run(decorate(a_func, b_decorator)) == "ba"

```
This expression apply ```b_decorator``` on function ```a_func```. 
Note that ```decorate(a_func, b_decorator)``` is not an async function, only action, or condition are async function.


Few guidelines of this implementation:

- In order to mimic all NodeStatus (success, failure, running), I replace this by truthy/falsy meaning of evaluation value.
  A special dedicated exception decorate standard exception in order to give them a Falsy meaning.
- Blackboard pattern, act as a manager of context variable for behavior tree.
  With python 3, please... simply use [contextvars](https://docs.python.org/3/library/contextvars.html) !
- In order to be able to build a sematic tree, I've introduce a metadata tuple added on function implementation.

The rest is just implementation details..



A little note:

> You should not use this until you're ready to think about what you're doing :)


### Note about 'async' framework

As we use async function as underlaying mechanism to manage the execution flow, the standard library asyncio is pretty fine.
But, (always a but somewhere isn't it...), you should read this [amazing blog post}(https://vorpus.org/blog/some-thoughts-on-asynchronous-api-design-in-a-post-asyncawait-world/) by Nathaniel J. Smith.
And next study [curio](https://github.com/dabeaz/curio) framework in deep.

As curio say:
> Don't Use Curio if You're Allergic to Curio

Personaly, after few time of testing and reading curio code, I'm pretty addict.


# Setup

## Requirements

* Python 3.7+

## Installation

Install this library directly into an activated virtual environment:

```text
$ pip install async-btree
```

or add it to your [Poetry](https://poetry.eustace.io/) project:

```text
$ poetry add async-btree
```

# Usage

After installation, the package can imported:

```text
$ python
>>> import async_btree
>>> async_btree.__version__
```

# Contributing

You could find all information in Contributing page.

