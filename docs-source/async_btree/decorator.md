# analyze
```python
analyze(target: Union[Callable[..., Awaitable[Any]], Callable]) -> async_btree.analyze.Node
```
Analyze specified target and return a Node representation.

__Parameters__

- __target (CallableFunction)__: async function to analyze

__Returns__

`(Node)`: a node instance representation of target function

# async_btree.decorator
Decorator module define all decorator function node.
## alias
```python
alias(child: Union[Callable[..., Awaitable[Any]], Callable], name: str) -> Callable[[], Awaitable[Any]]
```
Define an alias on our child.

__Parameters__

- __child (CallableFunction)__: child function to decorate
- __name (str)__: name of function tree

__Returns__

`(AsyncInnerFunction)`: an awaitable function.

## decorate
```python
decorate(child: Union[Callable[..., Awaitable[Any]], Callable], decorator: Union[Callable[..., Awaitable[Any]], Callable], **kwargs) -> Callable[[], Awaitable[Any]]
```
Create a decorator.

Post process a child with specified decorator function.
First argument of decorator function must be a child.

This method implement a simple lazy evaluation.

__Parameters__

- __child (CallableFunction)__: child function to decorate
- __decorator (CallableFunction)__: awaitable target decorator
- __kwargs__: optional keyed argument to pass to decorator function

__Returns__

`(AsyncInnerFunction)`: an awaitable function which
    return decorator evaluation against child.

## always_success
```python
always_success(child: Union[Callable[..., Awaitable[Any]], Callable]) -> Callable[[], Awaitable[Any]]
```
Create a node which always return SUCCESS value.

__Parameters__

- __child (CallableFunction)__: child function to decorate

__Returns__

`(AsyncInnerFunction)`: an awaitable function which return child result if is truthy
    else SUCCESS (Any exception will be ignored).


## always_failure
```python
always_failure(child: Union[Callable[..., Awaitable[Any]], Callable]) -> Callable[[], Awaitable[Any]]
```
Produce a function which always return FAILURE value.

__Parameters__

- __child (CallableFunction)__: child function to decorate

__Returns__

`(AsyncInnerFunction)`: an awaitable function which return child result if is falsy
    else FAILURE, or a ControlFlowException if error occurs.


## is_success
```python
is_success(child: Union[Callable[..., Awaitable[Any]], Callable]) -> Callable[[], Awaitable[Any]]
```
Create a conditional node which test if child success.

__Parameters__

- __child (CallableFunction)__: child function to decorate

__Returns__

`(AsyncInnerFunction)`: an awaitable function which return SUCCESS if child
    return SUCCESS else FAILURE.
    An exception will be evaluated as falsy.

## is_failure
```python
is_failure(child: Union[Callable[..., Awaitable[Any]], Callable]) -> Callable[[], Awaitable[Any]]
```
Create a conditional node which test if child fail.

__Parameters__

- __child (CallableFunction)__: child function to decorate

__Returns__

`(AsyncInnerFunction)`: an awaitable function which return SUCCESS if child
    return FAILURE else FAILURE.
    An exception will be evaluated as a success.

## inverter
```python
inverter(child: Union[Callable[..., Awaitable[Any]], Callable]) -> Callable[[], Awaitable[Any]]
```
Invert node status.

__Parameters__

- __child (CallableFunction)__: child function to decorate

__Returns__

`(AsyncInnerFunction)`: an awaitable function which return SUCCESS if child
    return FAILURE else SUCCESS

## retry
```python
retry(child: Union[Callable[..., Awaitable[Any]], Callable], max_retry: int = 3) -> Callable[[], Awaitable[Any]]
```
Retry child evaluation at most max_retry time on failure until child succeed.

__Parameters__

- __child (CallableFunction)__: child function to decorate
- __max_retry (int)__: max retry count (default 3), -1 mean infinite retry

__Returns__

`(AsyncInnerFunction)`: an awaitable function which retry child evaluation
    at most max_retry time on failure until child succeed.
    If max_retry is reached, returns FAILURE or last exception.

## retry_until_success
```python
retry_until_success(child: Union[Callable[..., Awaitable[Any]], Callable]) -> Callable[[], Awaitable[Any]]
```
Retry child until success.

__Parameters__

- __child (CallableFunction)__: child function to decorate

__Returns__

`(AsyncInnerFunction)`: an awaitable function which try to evaluate child
    until it succeed.

## retry_until_failed
```python
retry_until_failed(child: Union[Callable[..., Awaitable[Any]], Callable]) -> Callable[[], Awaitable[Any]]
```
Retry child until failed.

__Parameters__

- __child (CallableFunction)__: child function to decorate

__Returns__

`(AsyncInnerFunction)`: an awaitable function which try to evaluate child
    until it failed.

