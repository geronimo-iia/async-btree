"""
Common definition
"""
# from collections import namedtuple
from typing import Awaitable, Callable, List, NamedTuple, TypeVar, Union, Any


__all__ = [
    'CallableFunction',
    'AsyncInnerFunction',
    'SUCCESS',
    'FAILURE',
    'ExceptionDecorator',
    'NodeMetadata',
    'node_metadata',
]


CallableFunction = Union[Awaitable[Callable], Callable]
"""Something callable with or without async."""

AsyncInnerFunction = Awaitable[Callable[[], Any]]
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


T = TypeVar('T', covariant=True, bound=CallableFunction)


def node_metadata(  # pylint: disable=protected-access
    name: str = None, properties: List[str] = None, edges: List[str] = None
):
    """'node_metadata' is a function decorator which add meta information about node:
        - name
        - properties
        - edges
    We add a property on decorated function named '__node_metadata'.

    # Parameters
    name (str): override name of decorated function,
        default is function name left striped with '_'
    properties (List[str]): a list of property name ([] as default)
    edges (List[str]): a list of edges name (["child", "children"] as default)

    # Returns
    the decorator function
    """

    def decorate_function(function: T) -> T:
        function.__node_metadata = NodeMetadata(
            name=name if name else function.__name__.lstrip("_"),
            properties=properties or [],
            edges=edges or ["child", "children"],
        )
        return function

    return decorate_function
