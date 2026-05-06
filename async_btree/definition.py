"""Common definition.

CallableFunction Type:

Specify something callable with or without async:

```CallableFunction = Union[Callable[..., Awaitable[Any]], Callable]```

Function signature of async function implementation:

```AsyncInnerFunction = Callable[[], Awaitable[Any]]```

"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import (
    Any,
    NamedTuple,
    Protocol,
    TypeVar,
    cast,
)

from typing_extensions import ParamSpec

__all__ = [
    "FAILURE",
    "SUCCESS",
    "AsyncCallableFunction",
    "AsyncInnerFunction",
    "CallableFunction",
    "ControlFlowException",
    "NodeMetadata",
    "alias_node_metadata",
    "get_function_name",
    "get_node_metadata",
    "node_metadata",
]


CallableFunction = Callable[..., Awaitable[Any]] | Callable
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
    """Wraps an exception to give it falsy meaning without losing the original cause.

    Instances are always falsy (`bool(e)` returns `False`), so they can be
    returned as a FAILURE status while still carrying the original exception.
    """

    def __init__(self, exception: Exception):
        """Initialize with the original exception.

        Args:
            exception (Exception): the original exception to wrap.
        """
        super().__init__()

        self.exception = exception

    def __bool__(self):
        return False

    def __repr__(self):
        return self.exception.__repr__()

    def __str__(self):
        return self.exception.__str__()

    @classmethod
    def instantiate(cls, exception: Exception) -> ControlFlowException:
        """Return `exception` unchanged if already a `ControlFlowException`, otherwise wrap it.

        Args:
            exception (Exception): the exception to wrap if needed.

        Returns:
            (ControlFlowException): a falsy exception suitable for use as FAILURE.
        """
        return exception if isinstance(exception, ControlFlowException) else ControlFlowException(exception=exception)


class NodeMetadata(NamedTuple):
    """Metadata attached to a node function describing its name, properties, and child edges.

    Used by `analyze()` and `stringify_analyze()` to build and display the abstract tree.

    Attributes:
        name (str): display name of the node.
        properties (List[str] | None): names of scalar attributes to include in the tree view.
        edges (List[str] | None): names of child-bearing attributes. When `None`, `analyze()`
            falls back to `["child", "children", "_child", "_children"]`.
    """

    name: str
    properties: list[str] | None = None
    edges: list[str] | None = None

    @classmethod
    def alias(cls, name: str, node: NodeMetadata, properties: list[str] | None = None) -> NodeMetadata:
        """Return a copy of `node` with a new name and optional property override.

        Args:
            name (str): new display name.
            node (NodeMetadata): source metadata to copy edges from.
            properties (List[str] | None): if given, replaces `node.properties`.

        Returns:
            (NodeMetadata): new instance with updated name and properties.
        """
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
    name: str | None = None,
    properties: list[str] | None = None,
    edges: list[str] | None = None,
) -> Callable[[Callable[P, R]], FunctionWithMetadata[P, R]]:
    """Decorator that attaches `NodeMetadata` to a function as `__node_metadata`.

    Args:
        name (Optional[str]): override display name; defaults to the function name
            left-stripped of leading underscores.
        properties (Optional[List[str]]): names of scalar attributes to expose in the tree view.
        edges (Optional[List[str]]): names of child-bearing attributes. When `None`, `analyze()`
            falls back to `["child", "children", "_child", "_children"]`.

    Returns:
        the decorator function.
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
        return cast("FunctionWithMetadata[P, R]", dfunc)

    return decorate_function


def get_node_metadata(target: CallableFunction) -> NodeMetadata:
    """Return the `NodeMetadata` instance attached to `target`.

    Args:
        target (CallableFunction): function decorated with `@node_metadata`.

    Returns:
        (NodeMetadata): the metadata attached to `target`.

    Raises:
        RuntimeError: if `target` has no `__node_metadata` attribute, or if it is
            not a `NodeMetadata` instance.
    """
    node = getattr(target, "__node_metadata", False)
    if not isinstance(node, NodeMetadata):
        raise RuntimeError(f"attr __node_metadata of {target} is not a NodeMetadata!")
    return cast("NodeMetadata", node)


def alias_node_metadata(target: CallableFunction, name: str, properties: list[str] | None = None) -> CallableFunction:
    """Mutate `target.__node_metadata` in place to apply an alias name and optional properties.

    Args:
        target (CallableFunction): function whose `__node_metadata` will be updated.
        name (str): new display name to assign.
        properties (Optional[List[str]]): if given, replaces the existing properties list.

    Returns:
        (CallableFunction): `target` with its `__node_metadata` updated.
    """
    dfunc = _attr_decorator(target)
    dfunc.__node_metadata = NodeMetadata.alias(name=name, node=dfunc.__node_metadata, properties=properties)
    return dfunc
