"""Device-detect domain — fire-and-forget node discovery.

Request:  {"id": <int>, "t": <type>}
Response: none (the real hub does not acknowledge a detect broadcast).
"""
from __future__ import annotations

from simulator.state import HubState


def handle(state: HubState, msg: dict) -> None:
    state.detected.append({"id": msg.get("id"), "t": msg.get("t")})
    return None
