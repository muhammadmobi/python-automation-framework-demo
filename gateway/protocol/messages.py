"""Message builders — the single place that knows the MHub wire format.

Page Objects express intent ("create a scene that turns on these switches");
these builders turn that into the exact JSON the protocol expects. Keeping the
shapes here (not inline in pages or tests) is what makes the suite data-driven
and refactor-safe.
"""
from __future__ import annotations

import datetime
from typing import Iterable

# Command codes (mirror config.json["command"]).
CREATE, EDIT, DELETE, RUN = 1, 2, 3, 4


def _device_entry(node_id, s_value) -> dict:
    return {"id": node_id, "s": s_value}


# ── Scene ────────────────────────────────────────────────────────────────────
def create_scene(sid: int, group: str, node_id, s_value, cmd: int = CREATE) -> dict:
    return {"cmd": cmd, "sid": sid, "devices": {group: [_device_entry(node_id, s_value)]}}


def run_scene(sid: int, cmd: int = RUN) -> dict:
    return {"cmd": cmd, "sid": sid}


def delete_scene(sid: int, cmd: int = DELETE) -> dict:
    return {"cmd": cmd, "sid": sid}


def edit_scene(sid: int, *, edit=None, add=None, delete=None, cmd: int = EDIT) -> dict:
    msg: dict = {"cmd": cmd, "sid": sid}
    if edit is not None:
        msg["edit"] = {"devices": edit}
    if add is not None:
        msg["add"] = {"devices": add}
    if delete is not None:
        msg["delete"] = delete
    return msg


# ── Shadow (direct node control) ─────────────────────────────────────────────
def shadow_update(node_id: str, s_value) -> dict:
    return {"state": {"desired": {node_id: {"s": s_value}}}}


# ── Device configuration ─────────────────────────────────────────────────────
def configure_node(node_id: int, node_type: str, d_id: str, *, code: int | None = 5, **fields) -> dict:
    msg = {"id": node_id, "t": node_type, "d_id": d_id}
    if code is not None:
        msg["code"] = code
    msg.update(fields)  # bl=.. / th=.. / ol=..
    return msg


def detect_device(node_id: int, node_type: str) -> dict:
    return {"id": node_id, "t": node_type}


# ── Automation ───────────────────────────────────────────────────────────────
def create_automation(aid: int, sid: int, devices: dict, *, duration_min: int = 5, cmd: int = CREATE) -> dict:
    now = datetime.datetime.now()
    st = (now + datetime.timedelta(minutes=1)).timestamp()
    et = (now + datetime.timedelta(minutes=1 + duration_min)).timestamp()
    return {
        "aid": aid,
        "sid": sid,
        "md": {"devices": devices},
        "cmd": cmd,
        "time": {"st": st, "et": et, "d": 127},
        "at": 2,
    }


def edit_automation(aid: int, sid: int, *, add=None, edit=None, cmd: int = EDIT) -> dict:
    endpoints: dict = {}
    if add is not None:
        endpoints["add"] = {"devices": add}
    if edit is not None:
        endpoints["edit"] = {"devices": edit}
    return {"aid": aid, "sid": sid, "cmd": cmd, "at": 2, "md": {"endpoints": endpoints}}


def delete_automation(aid: int, sid: int, cmd: int = DELETE) -> dict:
    return {"aid": aid, "sid": sid, "cmd": cmd, "at": 2}


def devices_group(*entries: Iterable) -> list:
    """Helper: build a ``[{"id":.., "s":..}, ...]`` device list."""
    return [_device_entry(node_id, s_value) for node_id, s_value in entries]
