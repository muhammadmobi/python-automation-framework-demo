"""Device configuration domain — backlight / touch threshold / on-state level.

Request:  {"id": <int>, "t": <type>, "code": 5, "bl"|"th"|"ol": <v>, "d_id": ...}
Response: echoes the changed field plus {"rc": 0}.
"""
from __future__ import annotations

from simulator.state import HubState

OK = 0


def handle(state: HubState, msg: dict) -> dict:
    node_id = str(msg.get("id"))
    cfg = state.config_for(node_id)
    response = {"id": msg.get("id"), "t": msg.get("t"), "rc": OK}

    if "bl" in msg:
        cfg.backlight = msg["bl"]
        response["bl"] = msg["bl"]
    if "th" in msg:
        cfg.threshold = msg["th"]
        response["th"] = msg["th"]
    if "ol" in msg:
        cfg.onstate_level = msg["ol"]
        response["ol"] = msg["ol"]

    return response
