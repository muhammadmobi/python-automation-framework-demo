"""Scene domain — Create / Edit / Run / Delete.

Request:  {"cmd": <1|2|3|4>, "sid": <int>, "devices"|"add"|"edit"|"delete": ...}
Response: {"cmd": <same>, "sid": <same>, "rc": 0}   (rc != 0 on failure)
"""
from __future__ import annotations

from simulator.state import HubState

CREATE, EDIT, DELETE, RUN = 1, 2, 3, 4

OK, ERR = 0, 1


def handle(state: HubState, msg: dict) -> dict:
    cmd = msg.get("cmd")
    sid = msg.get("sid")
    rc = ERR

    if cmd == CREATE:
        state.scenes[sid] = {"devices": msg.get("devices", {})}
        rc = OK
    elif cmd == EDIT:
        if sid in state.scenes:
            scene = state.scenes[sid]
            if "add" in msg:
                scene.setdefault("devices", {}).update(msg["add"].get("devices", {}))
            if "edit" in msg:
                scene.setdefault("devices", {}).update(msg["edit"].get("devices", {}))
            for node_id in msg.get("delete", []):
                _remove_node(scene, node_id)
            rc = OK
    elif cmd == RUN:
        rc = OK if sid in state.scenes else ERR
    elif cmd == DELETE:
        rc = OK if state.scenes.pop(sid, None) is not None else ERR

    return {"cmd": cmd, "sid": sid, "rc": rc}


def _remove_node(scene: dict, node_id) -> None:
    for devices in scene.get("devices", {}).values():
        devices[:] = [d for d in devices if d.get("id") != node_id]
