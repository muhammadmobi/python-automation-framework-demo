"""Automation domain — time-window Create / Edit / Delete.

Request:  {"aid": <int>, "sid": <int>, "cmd": <1|2|3>, "at": 2,
           "md": {...}, "time": {"st": .., "et": .., "d": 127}}
Response: {"aid": <int>, "sid": <int>, "rc": 0, "devices": [{"id": .., "rc": 0}]}
"""
from __future__ import annotations

from simulator.state import HubState
from simulator.handlers.scene import CREATE, EDIT, DELETE, OK, ERR


def handle(state: HubState, msg: dict) -> dict:
    cmd = msg.get("cmd")
    aid = msg.get("aid")
    sid = msg.get("sid")

    if cmd == CREATE:
        state.automations[aid] = msg
        rc = OK
    elif cmd == EDIT:
        rc = OK if aid in state.automations else ERR
    elif cmd == DELETE:
        rc = OK if state.automations.pop(aid, None) is not None else ERR
    else:
        rc = ERR

    devices = [
        {"id": device.get("id"), "rc": OK}
        for device in _iter_devices(msg)
    ]
    return {"aid": aid, "sid": sid, "rc": rc, "devices": devices}


def _iter_devices(msg: dict):
    md = msg.get("md", {})
    groups = [md.get("devices", {})]
    endpoints = md.get("endpoints", {})
    for section in ("add", "edit"):
        groups.append(endpoints.get(section, {}).get("devices", {}))
    for group in groups:
        for device_list in group.values():
            yield from device_list
