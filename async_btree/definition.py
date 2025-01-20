"""Common definition.

CallableFunction Type:

Specify something callable with or without async:

```CallableFunction = Union[Callable[..., Awaitable[Any]], Callable]```

Function signature of async function implementation:

```AsyncInnerFunction = Callable[[], Awaitable[Any]]```

"""

from __future__ import annotations

from collections.abc import Awaitable
from typing import (
    Any,
    Callable,
    List,
    NamedTuple,
    Optional,
    Protocol,
    TypeVar,
    Union,
    cast,
)

from typing_extensions import ParamSpec

__all__ = [
    "CallableFunction",
    "AsyncInnerFunction",
    "AsyncCallableFunction",
    "SUCCESS",
    "FAILURE",
    "ControlFlowException",
    "NodeMetadata",
    "node_metadata",
    "get_node_metadata",
    "alias_node_metadata",
    "get_function_name",
]


CallableFunction = Union[Callable[..., Awaitable[Any]], Callable]
"""Something callable with or without async."""

AsyncInnerFunction = Callable[[], Awaitable[Any]]
"""Function signature of async function implementation."""

AsyncCallableFunction = Callable[..., Awaitable[Any]]
"""Async callable."""


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

    @classmethod
    def alias(cls, name: str, node: NodeMetadata, properties: Optional[List[str]] = None) -> NodeMetadata:
        return NodeMetadata(
            name=name,
            properties=properties if properties else node.properties,
            edges=node.edges,
        )


T = TypeVar("T", bound=Callable[..., Awaitable[Any]])

P = ParamSpec("P")
R = TypeVar("R", covariant=True)


class FunctionWithMetadata(Protocol[P, R]):
    __node_metadata: NodeMetadata

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R: ...


def _attr_decorator(func: Any) -> FunctionWithMetadata:
    """Deals with mypy.

    See https://github.com/python/mypy/issues/2087#issuecomment-1433069662
    """
    return func


def get_function_name(target: Callable, default_name: str = "anonymous") -> str:
    """Returns a function name.

    Args:
        target (CallableFunction): function to analyze.
        default_name (str): default name 'anonymous'

    Returns:
        (str): function name

    """
    return getattr(target, "__name__", default_name).lstrip("_")


def node_metadata(
    name: Optional[str] = None,
    properties: Optional[List[str]] = None,
    edges: Optional[List[str]] = None,
) -> Callable[[Callable[P, R]], FunctionWithMetadata[P, R]]:
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

    def decorate_function(function: Callable[P, R]) -> FunctionWithMetadata[P, R]:
        dfunc = _attr_decorator(function)

        dfunc.__node_metadata = getattr(
            dfunc,
            "__node_metadata",
            NodeMetadata(
                name=name if name else get_function_name(target=dfunc),
                properties=properties,
                edges=edges,
            ),
        )
        return cast(FunctionWithMetadata[P, R], dfunc)

    return decorate_function


def get_node_metadata(target: CallableFunction) -> NodeMetadata:
    """Returns node metadata instance associated with target."""
    node = getattr(target, "__node_metadata", False)
    if not isinstance(node, NodeMetadata):
        raise RuntimeError(f"attr __node_metadata of {target} is not a NodeMetadata!")
    return cast(NodeMetadata, node)


def alias_node_metadata(
    target: CallableFunction, name: str, properties: Optional[List[str]] = None
) -> CallableFunction:
    """Returns an aliased name of current metadata node.


    Args:
        target (CallableFunction): function to analyze.
        name (str): alias name to set
        properties (Optional[List[str]]): Optional properties list to overrides.

    Returns:
        (CallableFunction): function with updated node metadata.
    """
    dfunc = _attr_decorator(target)
    dfunc.__node_metadata = NodeMetadata.alias(name=name, node=dfunc.__node_metadata, properties=properties)
    return dfunc
