"""Tutorial 1 code.


This sample should print:
Hello: John
battery ok
battery dbl check
GripperInterface Open
approach_object: house
GripperInterface Close

"""
import curio
import async_btree as bt


async def approach_object(name: str):
    print(f"approach_object: {name}")


def check_battery():
    print("battery ok")
    # you should return a success
    return bt.SUCCESS


def check_again_battery():
    print("battery dbl check")
    # you should return a success
    return bt.SUCCESS


async def say_hello(name: str):
    # This method should be used with bt.always_success decorator
    # no return as q falsy meaning
    print(f"Hello: {name}")


class GripperInterface:
    def __init__(self):
        self._open = False

    def open(self):
        print("GripperInterface Open")
        self._open = True

    def close(self):
        print("GripperInterface Close")
        self._open = False


gripper = GripperInterface()

b_tree = bt.sequence(
    children=[
        bt.always_success(child=bt.action(target=say_hello, name="John")),
        bt.action(target=check_battery),
        check_again_battery,  # this will be encapsulated at runtime
        bt.always_success(child=bt.action(target=gripper.open)),
        bt.always_success(child=bt.action(target=approach_object, name="house")),
        bt.always_success(child=bt.action(target=gripper.close)),
    ]
)


if __name__ == '__main__':
    curio.run(b_tree)
