"""A tiny, dependency-free in-process MQTT-style message bus.

Both the virtual hub and the test-side client connect to the same broker
instance. Delivery is synchronous: publishing a message invokes every matching
subscriber's callback inline. That makes the suite fully deterministic — there
is no network, no event loop and no flaky timing to wait on.

The broker speaks the same ``publish`` / ``subscribe(topic, callback)`` shape as
``AWSIoTMQTTClient`` so the production transport is a drop-in swap. MQTT single
(``+``) and multi-level (``#``) wildcards are supported for completeness, though
the MHub topics are fully-qualified once the device id is substituted.
"""
from __future__ import annotations

import threading
from typing import Callable, Dict, List

Callback = Callable[[str, bytes], None]


def _topic_matches(filter_: str, topic: str) -> bool:
    if filter_ == topic:
        return True
    f_parts = filter_.split("/")
    t_parts = topic.split("/")
    for i, f in enumerate(f_parts):
        if f == "#":
            return True
        if i >= len(t_parts):
            return False
        if f == "+":
            continue
        if f != t_parts[i]:
            return False
    return len(f_parts) == len(t_parts)


class InProcessBroker:
    """Synchronous pub/sub bus shared by the hub and the test client."""

    def __init__(self) -> None:
        self._subscriptions: Dict[str, List[Callback]] = {}
        self._lock = threading.RLock()

    def subscribe(self, topic_filter: str, callback: Callback) -> None:
        with self._lock:
            self._subscriptions.setdefault(topic_filter, []).append(callback)

    def publish(self, topic: str, payload: bytes) -> None:
        with self._lock:
            targets = [
                cb
                for flt, cbs in self._subscriptions.items()
                if _topic_matches(flt, topic)
                for cb in cbs
            ]
        # Invoke outside the lock so a callback may publish without deadlocking.
        for callback in targets:
            callback(topic, payload)

    def reset(self) -> None:
        with self._lock:
            self._subscriptions.clear()
