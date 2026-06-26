"""Device shadow domain — desired -> reported.

Mirrors the AWS IoT classic shadow contract used for direct node control.

Request:  {"state": {"desired": {<node>: {"s": [prev, applied]}}}}
Response: {"state": {"reported": {<node>: {"s": [prev, applied]}}}}

``s[1]`` is the applied switch/level value the tests assert on. Only *desired*
packets are acted upon; reported echoes back the applied state.
"""
from __future__ import annotations

from simulator.state import HubState


def handle(state: HubState, msg: dict) -> dict | None:
    desired = msg.get("state", {}).get("desired")
    if not desired:
        return None

    reported = {}
    for node_id, payload in desired.items():
        s_value = payload.get("s")
        state.node_switch[node_id] = s_value
        reported[node_id] = {"s": s_value}

    return {"state": {"reported": reported}}
