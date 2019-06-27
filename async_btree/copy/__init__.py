"""
Control flow definition.

When you study advanced behavior tree, reactive node, dynamic change,
runtime implementation, etc ... at a moment you're build more or less something
that mimic an evaluator 'eval/apply' or a compilator.
Complexity came with internal state management, global variable, callback etc ...

What I find usefull with behavior tree:
 - clarity of expression
 - node tree representation
 - possibility to reuse behavior
 - add external measure to dynamicaly change a behavior


In this module, I purpose to use the concept of coroutine, and mecanism to
manage the execution flow.
By this way:
 - we reuse simple language mechanism to manage state, parameter, etc
 - no contraint on action implementation
 - most of language build could be reused
 - ...

In order to mimic all NodeStatus (success, failure, running), I replace this by
truthy/falsy meaning of evaluation value.
A special dedicated exception decorate standard exception in order to give them a Falsy meaning.

For all context variable of a behavior, please... use contextvars !
Use context var to process few system request https://docs.python.org/3/library/contextvars.html
Actually I not able to use context vars with curio, but it just a time problem.


As I've used OOP for two long time, I will try to avoid class tree and prefer using the power of
a single function to obtain what I want: metada on a sematic construc.
In order to be able to build a sematic tree, I've introduce a metadata tuple.
The rest is just implementation details..

So let's start.

A little note:
You should not use this until you're ready to think about what you're doing :)

"""
from .common import (
    amap,
    afilter,
    SUCCESS,
    FAILURE,
    ControlFlowException,
    ANode,
    node_metadata,
    analyze,
    print_analyze,
)
from .leaf import action, condition
from .control import sequence, fallback, selector, decision, repeat_until
from .decorator import (
    alias,
    decorate,
    always_success,
    always_failure,
    is_success,
    is_failure,
    inverter,
    retry,
    retry_until_success,
    retry_until_failed,
)

__all__ = [
    "amap",
    "afilter",
    "SUCCESS",
    "FAILURE",
    "ControlFlowException",
    "ANode",
    "node_metadata",
    "analyze",
    "print_analyze",
    "action",
    "condition",
    "sequence",
    "fallback",
    "selector",
    "decision",
    "repeat_until",
    "alias",
    "decorate",
    "always_success",
    "always_failure",
    "is_success",
    "is_failure",
    "inverter",
    "retry",
    "retry_until_success",
    "retry_until_failed",
]
