# analyze
```python
analyze(target: Union[Callable[..., Awaitable[Any]], Callable]) -> async_btree.analyze.Node
```
Analyze specified target and return a Node representation.

__Parameters__

- __target (CallableFunction)__: async function to analyze

__Returns__

`(Node)`: a node instance representation of target function

# parallele
```python
parallele(children: List[Union[Callable[..., Awaitable[Any]], Callable]], succes_threshold: int = -1) -> Callable[[], Awaitable[Any]]
```
Return an awaitable function which run children in parallele.

`succes_threshold` parameter generalize traditional sequence/fallback,
and must be in [0, len(children)], default value is len(children)

if `success` = succes_threshold, return a success

if `failure` = len(children) - succes_threshold, return a failure

__Parameters__

- __children (List[CallableFunction])__: list of Awaitable
- __succes_threshold (int)__: succes threshold value, default len(children)

__Returns__

`(AsyncInnerFunction)`: an awaitable function.


