"""Analyze definition."""
from inspect import getclosurevars
from typing import Any, Callable, List, NamedTuple, Optional, Tuple, no_type_check

from .definition import CallableFunction, NodeMetadata

__all__ = ["analyze", "stringify_analyze", "Node"]


class Node(NamedTuple):
    """Node aggregate node definition implemented with NamedTuple.

    A Node is used to keep information on name, properties, and relations ship
    between a hierachical construct of functions.
    It's like an instance of NodeMetadata.

    Attributes:
        name (str): named operation.
        properties (List[Tuple[str, Any]]): a list of tuple (name, value) for definition.
        edges (List[Tuple[str, List[Any]]]): a list of tuple (name, node list) for
            definition.

    Notes:
        Edges attribut should be edges: ```List[Tuple[str, List['Node']]]```
        But it is impossible for now, see [mypy issues 731](https://github.com/python/mypy/issues/731)
    """

    name: str
    properties: List[Tuple[str, Any]]
    # edges: List[Tuple[str, List['Node']]]
    # https://github.com/python/mypy/issues/731
    edges: List[Tuple[str, List[Any]]]

    def __str__(self):
        return stringify_analyze(target=self)


def _get_analyze_edges(nonlocals) -> Callable:

    return _get_analyze_edges


@no_type_check
def _get_node_metadata(target: CallableFunction) -> NodeMetadata:
    """Returns node metadata instance associated with target."""
    node = target.__node_metadata
    if not isinstance(node, NodeMetadata):
        raise RuntimeError(f'attr __node_metadata of {target} is not a NodeMetadata!')
    return node


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
        return nonlocals[name] if name in nonlocals else None

    def _analyze_property(p):
        """Return a tuple (name, value) or (name, function name) as property."""
        value = _get_nonlocals_value_for(name=p)
        return p, value.__name__ if value and callable(value) else value

    def _analyze_edges(egde_name):
        """Lookup children node from egde_name local var."""
        value = None
        edge = _get_nonlocals_value_for(name=egde_name)
        if edge:
            # it could be a collection of node
            if hasattr(edge, "__iter__"):
                value = list(map(analyze, edge))
            else:  # or a single node
                value = [analyze(edge)]
        return (egde_name, value)

    if hasattr(target, "__node_metadata"):
        node = _get_node_metadata(target=target)
        return Node(
            name=node.name,
            properties=list(map(_analyze_property, node.properties)),
            edges=list(filter(lambda p: p is not None, map(_analyze_edges, node.edges))),
        )

    # simple function
    return Node(
        name=target.__name__.lstrip("_") if hasattr(target, "__name__") else "anonymous",
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
    _ident = '    '
    _space = f'{_ident * indent} '
    result: str = ''
    if label:
        result += f'{_space}--({label})--> {target.name}:\n'
        _space += f"{_ident}{' ' * len(label)}"
    else:
        result += f'{_space}--> {target.name}:\n'

    for k, v in target.properties:
        result += f'{_space}    {k}: {v}\n'

    for _label, children in target.edges:
        if children:
            for child in children:
                result += stringify_analyze(target=child, indent=indent + 1, label=_label)
    return result
