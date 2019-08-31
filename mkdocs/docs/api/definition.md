# async_btree.definition
Common definition.

## CallableFunction Type

Specify something callable with or without async:

```CallableFunction = Union[Callable[..., Awaitable[Any]], Callable]```

## AsyncInnerFunction Type

Function signature of async function implementation:

```Callable[[], Awaitable[Any]]```


## ExceptionDecorator
```python
ExceptionDecorator(self, exception: Exception)
```
ExceptionDecorator exception is a decorator on a real exception.

This will ensure that ```assert ExceptionDecorator.__bool__ == False```.
This permit to return exception as a 'FAILURE' status.

## NodeMetadata
```python
NodeMetadata(self, /, *args, **kwargs)
```
NodeMetadata is our node definition.

__Attributes:__

name (str): named operation
properties (List[str]): a list of property name.
edges (List[str]): a list of member name which act as edges.


## node_metadata
```python
node_metadata(name: Union[str, NoneType] = None, properties: Union[List[str], NoneType] = None, edges: Union[List[str], NoneType] = None)
```
'node_metadata' is a function decorator which add meta information about node.

We add a property on decorated function named '__node_metadata'.

__Parameters:__

name (Optional[str]): override name of decorated function,
    default is function name left striped with '_'
properties (Optional[List[str]]): a list of property name ([] as default)
edges (Optional[List[str]]): a list of edges name
    (["child", "children"] as default)

__Returns:__

    the decorator function


