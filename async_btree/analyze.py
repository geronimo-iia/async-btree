"""Analyze definition."""

from inspect import getclosurevars
from typing import Any, NamedTuple, Optional, no_type_check

from .definition import CallableFunction, get_function_name, get_node_metadata

__all__ = ["analyze", "stringify_analyze", "Node"]

_DEFAULT_EDGES = ["child", "children", "_child", "_children"]


class Node(NamedTuple):
    """Node aggregate node definition implemented with NamedTuple.

    A Node is used to keep information on name, properties, and relations ship
    between a hierachical construct of functions.
    It's like an instance of NodeMetadata.

    Attributes:
        name (str): named operation.
        properties (list[tuple[str, Any]]): a list of tuple (name, value) for definition.
        edges (list[tuple[str, list[Any]]]): a list of tuple (name, node list) for
            definition.

    Notes:
        Edges attribut should be edges: ```list[tuple[str, list['Node']]]```
        But it is impossible for now, see [mypy issues 731](https://github.com/python/mypy/issues/731)
    """

    name: str
    properties: list[tuple[str, Any]]
    # edges: list[tuple[str, list['Node']]]
    # https://github.com/python/mypy/issues/731
    edges: list[tuple[str, list[Any]]]

    def __str__(self):
        return stringify_analyze(target=self)


def _get_target_propertie_name(value):
    if value and callable(value):
        return (
            get_node_metadata(target=value).name
            if hasattr(value, "__node_metadata")
            else get_function_name(target=value)
        )
    return value


def _analyze_target_edges(edges):
    if edges:
        # it could be a collection of node or a single node
        return list(map(analyze, edges if hasattr(edges, "__iter__") else [edges]))
    return None


# pylint: disable=protected-access
@no_type_check  # it's a shortcut for hasattr ...
def analyze(target: CallableFunction) -> Node:
    """Analyze specified target and return a Node representation.

    Args:
        target (CallableFunction): async function to analyze.

    Returns:
        (Node): a node instance representation of target function
    """

    nonlocals = getclosurevars(target).nonlocals

    def _get_nonlocals_value_for(name):
        return nonlocals.get(name, None)

    def _analyze_property(p):
        """Return a tuple (name, value) or (name, function name) as property."""
        value = _get_nonlocals_value_for(name=p)
        return p.lstrip("_"), _get_target_propertie_name(value=value)

    def _analyze_edges(egde_name):
        """Lookup children node from egde_name local var."""
        edges = _get_nonlocals_value_for(name=egde_name)
        return (egde_name.lstrip("_"), _analyze_target_edges(edges=edges))

    if hasattr(target, "__node_metadata"):
        node = get_node_metadata(target=target)
        return Node(
            name=node.name,
            properties=list(map(_analyze_property, node.properties)) if node.properties else [],
            edges=list(
                filter(
                    lambda p: p is not None,
                    map(_analyze_edges, node.edges or _DEFAULT_EDGES),
                )
            ),
        )

    # simple function
    return Node(
        name=get_function_name(target=target),
        properties=list(map(_analyze_property, nonlocals.keys())),
        edges=[],
    )


def stringify_analyze(target: Node, indent: int = 0, label: Optional[str] = None) -> str:
    """Stringify node representation of specified target.

    Args:
        target (CallableFunction): async function to analyze.
        indent (int): level identation (default to zero).
        label (Optional[str]): label of current node (default None).

    Returns:
        (str): a string node representation.
    """
    _ident = "    "
    _space = f"{_ident * indent} "
    result: str = ""
    if label:
        result += f"{_space}--({label})--> {target.name}:\n"
        _space += f"{_ident}{' ' * len(label)}"
    else:
        result += f"{_space}--> {target.name}:\n"

    for k, v in target.properties:
        result += f"{_space}    {k}: {v}\n"

    for _label, children in target.edges:
        if children:
            for child in children:
                result += stringify_analyze(target=child, indent=indent + 1, label=_label)
    return result
