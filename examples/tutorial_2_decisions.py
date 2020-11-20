"""Tutorial 2 - how to use decisions


The behavior tree looks like:
 --> sequence:
     succes_threshold: 2
     --(children)--> decision:
         --(condition)--> is_name_set:
         --(success_tree)--> say_hello:
         --(failure_tree)--> sequence:
                             succes_threshold: 2
             --(children)--> ask_for_name:
             --(children)--> say_hello:
     --(children)--> some_action:

"""

import curio
import async_btree as bt
import contextvars


async def some_action():
    print("continue here...")
    return bt.SUCCESS


async def say_hello():
    print(f"Hello {name.get()}")
    return bt.SUCCESS


async def is_name_set():
    return name.get() != ""


async def ask_for_name():
    new_name = input("Hello, whats your name? \n")
    if new_name != "":
        name.set(new_name)
        return bt.SUCCESS
    else:
        return bt.FAILURE


name = contextvars.ContextVar('name', default="")

greet_with_name = bt.decision(
    condition=is_name_set, success_tree=say_hello, failure_tree=bt.sequence([ask_for_name, say_hello])
)

b_tree = bt.sequence(children=[greet_with_name, some_action])

if __name__ == '__main__':

    name = contextvars.ContextVar('name', default="")

    curio.run(b_tree)

    # You can take a look at the final behavior tree
    abstract_tree_tree_1 = bt.analyze(b_tree)
    print(bt.stringify_analyze(abstract_tree_tree_1))
