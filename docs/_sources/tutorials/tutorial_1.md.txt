# How to create a BehaviorTree


In this tutorial series, most of the time Actions will just print some information on console, but keep in mind that real "production" code would probably do something more complicated.


The source code of this tutorial is [example/tutorial_1.py](https://raw.githubusercontent.com/geronimo-iia/async-btree/master/examples/tutorial_1.py).


## How to create your own Action

Firt, you have to wrote your function (async or sync) as normal, like this:

```python
def approach_object(name: str):
    print(f"approach_object: {name}")

def check_battery():
    print("battery ok")

async def say_hello(name: str):
    print(f"Hello: {name}")

```

At this point, this is not (yet) a behavior action. To define an action, you have to use ```action``` function:

```python
import async_btree as bt

approach_house_object_action = bt.action(target=approach_object, name="house")

check_battery_action = bt.action(target=check_battery)

say_hello_john = bt.action(target=say_hello, name="John")

```


With a class like this one:

```python
class GripperInterface:

    def __init__():
        self._open = False
    

    def open(self):
        print("GripperInterface Open")
        self._open = True
    
    def close(self):
        print("GripperInterface Close")
        self._open = False

```
We can define action for these functions:
    - GripperInterface.open
    - GripperInterface.close


## Create a tree dynamically

We will build a sequence of actions like this one:
 - say hello
 - check battery
 - open gripper
 - approach object
 - close gripper

To do that, we need to use ```sequence``` methods.

```python

gripper = GripperInterface()

b_tree = bt.sequence(children= [
    bt.action(target=say_hello, name="John"),
    bt.action(target=check_battery),
    bt.action(target=gripper.open),
    bt.action(target=approach_object, name="house"),
    bt.action(target=gripper.close)
])

```

Run it:

```python
import curio 
curio.run(b_tree)
```

And you should see:

```text
Hello: John
```

Why we did not see other action ? It's because our first action did not return a success (something truthy).
So we could add a ```return True```, on each our function, like this:

```python
def approach_object(name: str):
    print(f"approach_object: {name}")
    return True
```

Or we could rewrote our behavior tree with specific status:


```python
b_tree = bt.sequence(children= [
    bt.always_success(child=bt.action(target=say_hello, name="John")),
    bt.always_success(child=bt.action(target=check_battery)),
    bt.always_success(child=bt.action(target=gripper.open)),
    bt.always_success(child=bt.action(target=approach_object, name="house")),
    bt.always_success(child=bt.action(target=gripper.close))
])
```
If we running it again:

```text
Hello: John
battery ok
GripperInterface Open
approach_object: house
GripperInterface Close
```

As you could see:
- we use a single instance of GripperInterface
- we have hard coded name on our action function

In a real use case, we should find a way to avoid this:
- wrote a factory function for a specific case
- either by using ContextVar (```from contextvars import ContextVar```)

You could see a sample in this source is [example/tutorial_2_decisions.py](https://raw.githubusercontent.com/geronimo-iia/async-btree/master/examples/tutorial_2_decisions.py).