# analyze
```python
analyze(target: Union[Callable[..., Awaitable[Any]], Callable]) -> async_btree.analyze.Node
```
Analyze specified target and return a Node representation.

__Parameters__

- __target (CallableFunction)__: async function to analyze

__Returns__

`(Node)`: a node instance representation of target function

# async_btree.utils
Utility function.
## amap
```python
amap(corofunc: Callable[[Any], Awaitable[~T]], iterable: Union[AsyncIterable, Iterable]) -> AsyncGenerator[~T, NoneType]
```
Map an async function onto an iterable or an async iterable.

__Parameters__

- __corofunc (Callable[[Any], Awaitable[T]])__: coroutine function
- __iterable (Union[AsyncIterable, Iterable])__: iterable or async iterable collection
    which will be applied.

__Returns__

`AsyncGenerator[T]`: an async iterator of corofunc(item)

__Example__

```[i async for i in amap(inc, afilter(even, [0, 1, 2, 3, 4]))]```


## afilter
```python
afilter(corofunc: Callable[[Any], Awaitable[bool]], iterable: Union[AsyncIterable, Iterable]) -> AsyncGenerator[~T, NoneType]
```
Filter an iterable or an async iterable with an async function.

__Parameters__

- __corofunc (Callable[[Any], Awaitable[bool]])__: filter async function
- __iterable (Union[AsyncIterable, Iterable])__: iterable or async iterable collection
    which will be applied.

__Returns__

`(AsyncGenerator[T])`: an async iterator of item which satisfy corofunc(item) == True

__Example__

```[i async for i in amap(inc, afilter(even, [0, 1, 2, 3, 4]))]```


## run
```python
run(kernel, target, *args)
```
Curio run with independent contextvars.
