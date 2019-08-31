# analyze
```python
analyze(target: Union[Callable[..., Awaitable[Any]], Callable]) -> async_btree.analyze.Node
```
Analyze specified target and return a Node representation.

__Parameters__

- __target (CallableFunction)__: async function to analyze

__Returns__

`(Node)`: a node instance representation of target function

# async_btree.leaf
Leaf definition.
## action
```python
action(target: Union[Callable[..., Awaitable[Any]], Callable], **kwargs) -> Callable[[], Awaitable[Any]]
```
Declare an action leaf.

Action is an awaitable closure of specified function.

__Parameters__

- __target (CallableFunction)__: awaitable function
- __kwargs__: optional kwargs argument to pass on target function

__Returns__

`(AsyncInnerFunction)`: an awaitable function.

## condition
```python
condition(target: Union[Callable[..., Awaitable[Any]], Callable], **kwargs) -> Callable[[], Awaitable[Any]]
```
Declare a condition leaf.

Condition is an awaitable closure of specified function.

__Parameters__

- __target (CallableFunction)__:  awaitable function which be evaluated as True/False.
- __kwargs__: optional kwargs argument to pass on target function

__Returns__

`(AsyncInnerFunction)`: an awaitable function.

