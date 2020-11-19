"""Common definition.

CallableFunction Type:

Specify something callable with or without async:

```CallableFunction = Union[Callable[..., Awaitable[Any]], Callable]```

Function signature of async function implementation:

```AsyncInnerFunction = Callable[[], Awaitable[Any]]```

"""
# from collections import namedtuple
from typing import Any, Awaitable, Callable, List, NamedTuple, Optional, TypeVar, Union, no_type_check

__all__ = [
    'CallableFunction',
    'AsyncInnerFunction',
    'SUCCESS',
    'FAILURE',
    'ControlFlowException',
    'NodeMetadata',
    'node_metadata',
    'get_node_metadata',
]


CallableFunction = Union[Callable[..., Awaitable[Any]], Callable]
"""Something callable with or without async."""

AsyncInnerFunction = Callable[[], Awaitable[Any]]
"""Function signature of async function implementation."""

SUCCESS = True  # a success call
"""Success constant."""

FAILURE = not SUCCESS  # Well defined falsy...
"""Failure constant."""


class ControlFlowException(Exception):
    """ControlFlowException exception is a decorator on a real exception.

    This will ensure that ```assert ControlFlowException.__bool__ == False```.
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

    @classmethod
    def instanciate(cls, exception: Exception):
        # this methods simplify usage of hierarchical call tree.
        return exception if isinstance(exception, ControlFlowException) else ControlFlowException(exception=exception)


class NodeMetadata(NamedTuple):
    """NodeMetadata is our node definition.

    A NodeMetadata is used to keep information on name, properties name,
    and relations ship name between a hierachical construct of functions.

    This permit us to print or analyze all information of a behaviour tree.

    Attributes:
        name (str): named operation
        properties (List[str]): a list of property name (an int value, ...).
        edges (List[str]): a list of member name which act as edges (a child, ...).

    """

    name: str
    properties: Optional[List[str]] = None
    edges: Optional[List[str]] = None


T = TypeVar('T', bound=CallableFunction)


def node_metadata(
    name: Optional[str] = None, properties: Optional[List[str]] = None, edges: Optional[List[str]] = None
):
    """'node_metadata' is a function decorator which add meta information about node.

    We add a property on decorated function named '__node_metadata'.

    Args:
        name (Optional[str]): override name of decorated function,
            default is function name left striped with '_'
        properties (Optional[List[str]]): a list of property name ([] as default)
        edges (Optional[List[str]]): a list of edges name
            (["child", "children"] as default)

    Returns:
        the decorator function

    """

    def decorate_function(function: T) -> T:
        function.__node_metadata = NodeMetadata(
            name=name if name else function.__name__.lstrip('_'), properties=properties, edges=edges
        )
        return function

    return decorate_function


@no_type_check
def get_node_metadata(target: CallableFunction) -> NodeMetadata:
    """Returns node metadata instance associated with target."""
    node = target.__node_metadata
    if not isinstance(node, NodeMetadata):
        raise RuntimeError(f'attr __node_metadata of {target} is not a NodeMetadata!')
    return node
