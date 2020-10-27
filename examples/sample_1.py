import curio
import async_btree as bt
import contextvars

name = contextvars.ContextVar('name',default="")

def some_action():
    print("continue here...")

async def say_hello():
    print(f"Hello: {name.get()}")

async def is_name_set():
    print("current name is " + name.get())
    return name.get() != ""



greet_with_name = bt.decision(is_name_set, 
        bt.always_success(child=bt.action(target=say_hello))        
        )

b_tree = bt.sequence(
    children=[
        greet_with_name,        
        bt.always_success(child=bt.action(target=some_action)),        
    ]
)

if __name__ == '__main__':
       
    name = contextvars.ContextVar('name')
    name.set("Hans")    
  
    curio.run(b_tree)

    abstract_tree_tree_1 = bt.analyze(b_tree) 
    # output the tree:
    print(bt.stringify_analyze(abstract_tree_tree_1))