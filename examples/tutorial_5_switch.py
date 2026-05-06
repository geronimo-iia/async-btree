"""Tutorial 5 - routing with switch

A robot reads a sensor mode and routes to the appropriate action.
The behavior tree looks like:

 --> sequence:
     success_threshold: 2
     --(children)--> switch:
                     case_keys: ['idle', 'patrol', 'attack']
         --(default)--> unknown_mode:
     --(children)--> report_done:

"""

from contextvars import ContextVar

import async_btree as bt

mode: ContextVar[str] = ContextVar("mode", default="idle")


async def get_mode() -> str:
    return mode.get()


async def handle_idle() -> bool:
    print("Robot is idle.")
    return bt.SUCCESS


async def handle_patrol() -> bool:
    print("Robot is patrolling.")
    return bt.SUCCESS


async def handle_attack() -> bool:
    print("Robot is attacking!")
    return bt.SUCCESS


async def unknown_mode() -> bool:
    print(f"Unknown mode: {mode.get()!r}")
    return bt.FAILURE


async def report_done() -> bool:
    print("Action complete.")
    return bt.SUCCESS


router = bt.switch(
    condition=get_mode,
    cases={
        "idle": handle_idle,
        "patrol": handle_patrol,
        "attack": handle_attack,
    },
    default=unknown_mode,
)

b_tree = bt.sequence(children=[router, report_done])

if __name__ == "__main__":
    # Each bt.run() call captures the current ContextVar state at call time,
    # so setting mode before each run works correctly.
    for m in ["idle", "patrol", "attack", "recharge"]:
        mode.set(m)
        print(f"\n--- mode={m!r} ---")
        bt.run(b_tree)

    print()
    print(bt.stringify_analyze(bt.analyze(b_tree)))
