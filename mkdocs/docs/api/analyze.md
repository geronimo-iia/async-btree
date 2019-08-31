# analyze
```python
analyze(target: Union[Callable[..., Awaitable[Any]], Callable]) -> async_btree.analyze.Node
```
Analyze specified target and return a Node representation.

__Parameters__

- __target (CallableFunction)__: async function to analyze

__Returns__

`(Node)`: a node instance representation of target function

# stringify_analyze
```python
stringify_analyze(target: async_btree.analyze.Node, indent: int = 0, label: Union[str, NoneType] = None) -> str
```
Stringify node representation of specified target.

__Parameters__

- __target (CallableFunction)__: async function to analyze
- __indent (int)__: level identation (default to zero)
- __label (Optional[str])__: label of current node (default None)

__Returns__

`(str)`: a string node representation

# Node
```python
Node(self, /, *args, **kwargs)
```
Node aggregate node definition implemented with NamedTuple.

__Attributes__

- `name (str)`: named operation
- `properties (List[Tuple[str, Any]])`: a list of tuple (name, value) for definition.
- `edges (List[Tuple[str, List[Any]]])`: a list of tuple (name, node list) for
    definition.

__Notes__


Edges attribut should be edges: ```List[Tuple[str, List['Node']]]```

But it is impossible for now, see
[mypy issues 731](https://github.com/python/mypy/issues/731)

