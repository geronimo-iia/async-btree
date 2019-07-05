"""Analyze definition."""
from inspect import getclosurevars
from typing import Any, List, NamedTuple, Tuple, no_type_check

from .definition import CallableFunction, NodeMetadata


__all__ = ["analyze", "stringify_analyze", "Node"]


class Node(NamedTuple):
    """Node aggregate node definition.

    - name: named operation
    - properties: a list of tuple (name, value) for definition.
    - edges: a list of tuple (name, node list) for definition.
    """

    name: str
    properties: List[Tuple[str, Any]]
    # edges: List[Tuple[str, List['Node']]]
    # https://github.com/python/mypy/issues/731
    edges: List[Tuple[str, List[Any]]]

    def __str__(self):
        return stringify_analyze(a_node=self)


# pylint: disable=protected-access
@no_type_check  # it's a shortcut for hasattr ...
def analyze(target: CallableFunction) -> Node:
    """Analyze specified target and return a Node representation.

    # Parameters
    - target (CallableFunction): async function to analyze

    # Returns
    (Node) a defintion
    """

    nonlocals = getclosurevars(target).nonlocals

    def _analyze_property(p):
        """Return a tuple (name, value) or (name, function name) as property."""
        value = nonlocals[p] if p in nonlocals else None
        return p, value.__name__ if value and callable(value) else value

    def _analyze_edges(egde_name):
        """Lookup children node from egde_name local var."""
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
        if not isinstance(node, NodeMetadata):
            raise RuntimeError(
                f'attr __node_metadata of {target} is not a NodeMetadata!'
            )
        return Node(
            name=node.name,
            properties=list(map(_analyze_property, node.properties)),
            edges=list(
                filter(lambda p: p is not None, map(_analyze_edges, node.edges))
            ),
        )

    # simple function
    return Node(
        name=target.__name__.lstrip("_")
        if hasattr(target, "__name__")
        else "anonymous",
        properties=list(map(_analyze_property, nonlocals.keys())),
        edges=[],
    )


def stringify_analyze(a_node: Node, indent=0, label=None) -> str:
    """Print a textual representation of a Node."""
    _ident = '    '
    _space = f'{_ident * indent} '
    result: str = ''
    if label:
        result += f'{_space}--({label})--> {a_node.name}:\n'
        _space += f"{_ident}{' ' * len(label)}"
    else:
        result += f'{_space}--> {a_node.name}:\n'

    for k, v in a_node.properties:
        result += f'{_space}    {k}: {v}\n'

    for _label, children in a_node.edges:
        if children:
            for child in children:
                result += stringify_analyze(
                    a_node=child, indent=indent + 1, label=_label
                )
    return result
