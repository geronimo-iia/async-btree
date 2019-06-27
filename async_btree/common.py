"""
Common definition.

"""
from collections import namedtuple
from typing import List, Awaitable
from inspect import getclosurevars

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
]

async def amap(corofunc: Awaitable, iterable):
    """
    Async map.
    :param corofunc: coroutine function
    :param iterable: iterable or async iterable collection which will be applied.
    :return: an iterator of corofunc(item)
    """
    if hasattr(iterable, '__aiter__'):
        async for item in iterable:
            yield await corofunc(item)
    else:
        for item in iterable:
            yield await corofunc(item)

async def afilter(corofunc: Awaitable, iterable):
    """
    Async filter.
    :param corofunc: coroutine function (item) -> bool
    :param iterable: iterable or async iterable collection which will be applied.
    :return: an iterator of item which satisfy corofunc(item) == True
    """
    if hasattr(iterable, '__aiter__'):
        async for item in iterable:
            if await corofunc(item):
                yield item
    else:
        for item in iterable:
            if await corofunc(item):
                yield item


SUCCESS = True  # a success call


FAILURE = not SUCCESS  # Well defined falsy...


class ControlFlowException(BaseException):
    """
    ControlFlowException exception is a decorator on a real exception
    with the assert ControlFlowException.__bool__ == False.
    This permit to return exception as a 'FAILURE' status.
    """

    def __init__(self, exception):
        self.exception = exception

    def __bool__(self):
        return False


ANode = namedtuple("ANode", ["name", "properties", "edges"])
"""
ANode is our node defition AND node metadata:
 - name: named operation
 - properties: a list of property name (metadata), or a list of tuple (name, value) for definition.
 - edges: a list of member which act as edges (metadata), or a list of tuple (name, node list) for definition.

Implementation note:
 - is it better to define two namedtuple, on for each meaning: metadata and definition ?
"""


def node_metadata(name: str = None, properties: List[str] = None, edges: List[str] = None):
    """
    'node_metadata' is a function decorator which add meta information about node:
        - name
        - properties
        - edges
    We add a property on decorated function named '__node_metadata'.

    :param name: override name of decorated function, default is function name left striped with '_'
    :param properties: a list of property name ([] as default)
    :param edges: a list of edges name (["child", "children"] as default)
    :return: decorator function
    """

    def decorate_function(fn):
        fn.__node_metadata = ANode(
            name=name if name else fn.__name__.lstrip("_"),
            properties=properties or [],
            edges=edges or ["child", "children"]
        )
        return fn

    return decorate_function


def analyze(target: Awaitable) -> ANode:
    """
    Analyze specified target and return a dictionary representation.
    Each node have:
        - name,
        - properties list of tuple (name, value), 
        - egdes a list of tuple. Tuple is (name, node list)
    :param target: awaitable function to analyze
    :return: ANode defintion
    """

    nonlocals = getclosurevars(target).nonlocals

    def analyze_property(p):
        """
        Return a tuple (name, value) or (name, function name) as property
        """
        value = nonlocals[p] if p in nonlocals else None
        return p, value.__name__ if value and callable(value) else value

    def analyze_edges(egde_name):
        """
        Lookup children node from egde_name local var.
        """
        value = None
        if egde_name in nonlocals and nonlocals[egde_name]:
            edge = nonlocals[egde_name]
            # it could be a collection of node
            if hasattr(edge, "__iter__"):
                value = list(map(analyze, edge))
            else:  # or a single node
                value = [analyze(edge)]
        return (egde_name, value)

    if hasattr(target, "__node_metadata"):
        # its a node construct.
        node = target.__node_metadata
        return ANode(
            name=node.name,
            properties=list(map(analyze_property, node.properties)),
            edges=list(filter(lambda p: p is not None, map(analyze_edges, node.edges))),
        )
    # simple function
    return ANode(
        name=target.__name__.lstrip("_")
        if hasattr(target, "__name__")
        else "anonymous",
        properties=list(map(analyze_property, nonlocals.keys())),
        edges=[],
    )


def print_analyze(meta: ANode, indent=0, label=None):
    """
    Print a textual representation of a B_node.
    """
    _ident = '    '
    _space = f'{_ident * indent} '
    if label:
        print(f"{_space}--({label})--> {meta.name}:")
        _space += f"{_ident}{' ' * len(label)}"
    else:
        print(f"{_space}--> {meta.name}:")

    for k, v in meta.properties:
        print(f"{_space}    {k}: {v}")

    for label, children in meta.edges:
        if children:
            for child in children:
                print_analyze(meta=child, indent=indent + 1, label=label)
