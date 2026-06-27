"""Test-side MQTT client — the driver core.

A faithful, cleaned-up reimplementation of the original ``Driver/mqtt_client.py``:
subscribes to the four response topics, filters out device-initiated chatter
(``getScene`` / ``getAutomation`` polls and shadow ``desired`` echoes), and
exposes a blocking ``wait_for_response`` backed by a thread-safe queue. It is
transport-agnostic and holds no global state.
"""
from __future__ import annotations

import json
import queue

from gateway.driver.transport import Transport


class MqttClient:
    def __init__(self, transport: Transport, topics: dict) -> None:
        self._transport = transport
        self._topics = topics
        self._responses: "queue.Queue[dict]" = queue.Queue()

        sub = topics["subscription"]
        transport.subscribe(sub["scene"], self._on_scene)
        transport.subscribe(sub["ShadowAccepted"], self._on_shadow_accepted)
        transport.subscribe(sub["DeviceConfigure"], self._on_generic)
        transport.subscribe(sub["Automation"], self._on_automation)

    # ── inbound callbacks ────────────────────────────────────────────────────
    def _on_scene(self, _topic: str, payload: bytes) -> None:
        data = json.loads(payload.decode("utf-8"))
        if data.get("cmd") == 0 and data.get("request") == "getScene":
            return  # ignore device poll
        self._responses.put(data)

    def _on_shadow_accepted(self, _topic: str, payload: bytes) -> None:
        data = json.loads(payload.decode("utf-8"))
        if "desired" not in data.get("state", {}):  # only the reported packet
            self._responses.put(data)

    def _on_automation(self, _topic: str, payload: bytes) -> None:
        data = json.loads(payload.decode("utf-8"))
        if data.get("cmd") == 0 and data.get("request") == "getAutomation":
            return
        self._responses.put(data)

    def _on_generic(self, _topic: str, payload: bytes) -> None:
        self._responses.put(json.loads(payload.decode("utf-8")))

    # ── public API ───────────────────────────────────────────────────────────
    def publish(self, topic: str, message: dict) -> None:
        self._transport.publish(
            topic, json.dumps(message, separators=(",", ":")).encode("utf-8")
        )

    def request(self, topic: str, message: dict, timeout: int = 10) -> dict:
        self.publish(topic, message)
        return self.wait_for_response(timeout)

    def wait_for_response(self, timeout: int = 10) -> dict:
        try:
            return self._responses.get(block=True, timeout=timeout)
        except queue.Empty as exc:
            raise TimeoutError("No response received from hub") from exc

    def drain(self) -> None:
        while not self._responses.empty():
            self._responses.get_nowait()

    def disconnect(self) -> None:
        self._transport.disconnect()
