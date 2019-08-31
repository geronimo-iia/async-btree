# analyze
```python
analyze(target: Union[Callable[..., Awaitable[Any]], Callable]) -> async_btree.analyze.Node
```
Analyze specified target and return a Node representation.

__Parameters__

- __target (CallableFunction)__: async function to analyze

__Returns__

`(Node)`: a node instance representation of target function

# async_btree.control
Control function definition.
## sequence
```python
sequence(children: List[Union[Callable[..., Awaitable[Any]], Callable]], succes_threshold: int = -1) -> Callable[[], Awaitable[Any]]
```
Return a function which execute children in sequence.

succes_threshold parameter generalize traditional sequence/fallback and
must be in [0, len(children)]. Default value is (-1) means len(children)

if `success` = succes_threshold, return a success

if `failure` = len(children) - succes_threshold, return a failure

What we can return as value and keep sematic Failure/Success:
 - an array of previous result when success
 - last failure when fail

__Parameters__

- __children (List[CallableFunction])__: list of Awaitable
- __succes_threshold (int)__: succes threshold value

__Returns__

`(AsyncInnerFunction)`: an awaitable function.

__Exceptions:__

    AssertionError if succes_threshold is invalid

## fallback
```python
fallback(children: List[Union[Callable[..., Awaitable[Any]], Callable]]) -> Callable[[], Awaitable[Any]]
```
Execute tasks in sequence and succeed if one succeed or failed if all failed.

Often named 'selector', children can be seen as an ordered list
    starting from higthest priority to lowest priority.

__Parameters__

- __children (List[CallableFunction])__: list of Awaitable

__Returns__

`(AsyncInnerFunction)`: an awaitable function.

## selector
```python
selector(children: List[Union[Callable[..., Awaitable[Any]], Callable]]) -> Callable[[], Awaitable[Any]]
```
Synonym of fallback.
## decision
```python
decision(condition: Union[Callable[..., Awaitable[Any]], Callable], success_tree: Union[Callable[..., Awaitable[Any]], Callable], failure_tree: Union[Callable[..., Awaitable[Any]], Callable, NoneType] = None) -> Callable[[], Awaitable[Any]]
```
Create a decision node.

__Parameters__

- __condition (CallableFunction)__: awaitable condition
- __success_tree (CallableFunction)__: awaitable success tree which be
    evaluated if cond is Truthy
- __failure_tree (CallableFunction)__: awaitable failure tree which be
    evaluated if cond is Falsy (None per default)

__Returns__

`(AsyncInnerFunction)`: an awaitable function.

## repeat_until
```python
repeat_until(condition: Union[Callable[..., Awaitable[Any]], Callable], child: Union[Callable[..., Awaitable[Any]], Callable]) -> Callable[[], Awaitable[Any]]
```
Repeat child evaluation until condition is truthy.

Return last child evaluation or FAILURE if no evaluation occurs.

__Parameters__

- __condition (CallableFunction)__: awaitable condition
- __child (CallableFunction)__: awaitable child

__Returns__

`(AsyncInnerFunction)`: an awaitable function.

