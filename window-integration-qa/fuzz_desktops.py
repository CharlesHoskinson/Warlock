#!/usr/bin/env python3
"""Randomized checks for the real desktop and minimize backends under a mock compositor."""

import random

from test_windowctl import Environment, window


def verify(env):
    result, state = env.virtual_desktops("list")
    ids = [d["id"] for d in result["desktops"]]
    assert len(ids) == len(set(ids)) and ids
    assert result["active"] in ids
    for w in state["clients"]:
        home = w["workspace"]["name"]
        if home == "special:win-minimized":
            path = env.root / "runtime/hypr-windowctl" / w["address"]
            home = path.read_text().split()[0]
        assert home in ids, (home, ids)


def run(seed):
    rng = random.Random(seed)
    env = Environment([window("0xaaa"), window("0xbbb"), window("0xccc")])
    try:
        for _ in range(55):
            result, state = env.virtual_desktops("list")
            ids = [d["id"] for d in result["desktops"]]
            action = rng.choice(["new", "close", "switch", "move", "minimize", "restore", "rename", "reorder"])
            address = rng.choice(["0xaaa", "0xbbb", "0xccc"])
            if action == "new" and len(ids) < 6:
                env.virtual_desktops("new")
            elif action == "close" and len(ids) > 1:
                env.virtual_desktops("close", rng.choice(ids))
            elif action == "switch":
                env.virtual_desktops("switch", rng.choice(ids))
            elif action == "move":
                env.virtual_desktops("move", address, rng.choice(ids))
            elif action == "minimize":
                env.run("minimize", address)
            elif action == "restore":
                env.run("restore", address)
            elif action == "rename":
                env.virtual_desktops("rename", rng.choice(ids), "Project " + str(seed))
            elif action == "reorder" and len(ids) > 1:
                env.virtual_desktops("reorder", rng.choice(ids), rng.choice(ids))
            verify(env)
    finally:
        env.close()


if __name__ == "__main__":
    for seed in (7, 23, 101):
        run(seed)
    print("desktop backend fuzz: 165 mixed operations passed")
