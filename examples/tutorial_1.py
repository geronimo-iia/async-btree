"""Tutorial 1 code."""
import curio
import async_btree as bt


def approach_object(name: str):
    print(f"approach_object: {name}")


def check_battery():
    print("battery ok")


async def say_hello(name: str):
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
        bt.always_success(child=bt.action(target=check_battery)),
        bt.always_success(child=bt.action(target=gripper.open)),
        bt.always_success(child=bt.action(target=approach_object, name="house")),
        bt.always_success(child=bt.action(target=gripper.close)),
    ]
)


if __name__ == '__main__':
    curio.run(b_tree)
