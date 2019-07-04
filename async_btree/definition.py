"""Common definition."""
# from collections import namedtuple
from typing import Any, Awaitable, Callable, List, NamedTuple, Optional, TypeVar, Union


__all__ = [
    'CallableFunction',
    'AsyncInnerFunction',
    'SUCCESS',
    'FAILURE',
    'ExceptionDecorator',
    'NodeMetadata',
    'node_metadata',
]


CallableFunction = Union[Callable[..., Awaitable[Any]], Callable]
"""Something callable with or without async."""

AsyncInnerFunction = Callable[[], Awaitable[Any]]
"""Function signature of async function implementation."""

SUCCESS = True  # a success call
"""Success constant."""

FAILURE = not SUCCESS  # Well defined falsy...
"""Failure constant."""


class ExceptionDecorator(Exception):
    """ExceptionDecorator exception is a decorator on a real exception.

    This will ensure that ```assert ExceptionDecorator.__bool__ == False```.
    This permit to return exception as a 'FAILURE' status.
    """

    def __init__(self, exception: Exception):
        super().__init__()
        self.exception = exception

    def __bool__(self):
        return False

    def __repr__(self):
        return self.exception.__repr__()

    def __str__(self):
        return self.exception.__str__()


class NodeMetadata(NamedTuple):
    """NodeMetadata is our node definition.

    # Attributes
    - name (str): named operation
    - properties (List[str]): a list of property name.
    - edges (List[str]): a list of member name which act as edges.
    """

    name: str
    properties: List[str]
    edges: List[str]


T = TypeVar('T', bound=CallableFunction)


def node_metadata(
    name: Optional[str] = None,
    properties: Optional[List[str]] = None,
    edges: Optional[List[str]] = None,
):
    """'node_metadata' is a function decorator which add meta information about node.

    We add a property on decorated function named '__node_metadata'.

    # Parameters
    name (Optional[str]): override name of decorated function,
        default is function name left striped with '_'
    properties (Optional[List[str]]): a list of property name ([] as default)
    edges (Optional[List[str]]): a list of edges name (["child", "children"] as default)

    # Returns
    the decorator function
    """

    def decorate_function(function: T) -> T:
        function.__node_metadata = NodeMetadata(
            name=name if name else function.__name__.lstrip('_'),
            properties=properties or [],
            edges=edges or ['child', 'children'],
        )
        return function

    return decorate_function
