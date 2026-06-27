"""Base for every Page Object.

The MQTT analogue of the sibling demos' ``BasePage``. Where a UI BasePage
centralises the driver, explicit waits and tap/type helpers, this one centralises
the MQTT session and the publish / request / wait-for-response primitives — so
Page Objects stay declarative and tests never touch the transport, topic strings
or the response queue directly.
"""
from __future__ import annotations

from gateway.driver.driver_manager import DriverManager


class BasePage:
    def __init__(self) -> None:
        session = DriverManager.get_driver()
        self._mqtt = session.mqtt
        self._topics = session.topics
        self._timeout = session.timeout
        self.hub = session.hub  # present only for the offline virtual-hub target

    # ── topic helpers ────────────────────────────────────────────────────────
    def _pub_topic(self, key: str) -> str:
        return self._topics["publish"][key]

    # ── reusable actions ─────────────────────────────────────────────────────
    def publish(self, topic_key: str, message: dict) -> None:
        """Fire-and-forget publish (no response expected)."""
        self._mqtt.publish(self._pub_topic(topic_key), message)

    def request(self, topic_key: str, message: dict) -> dict:
        """Publish and return the next correlated response (the common case)."""
        return self._mqtt.request(self._pub_topic(topic_key), message, self._timeout)

    def wait_for_response(self) -> dict:
        return self._mqtt.wait_for_response(self._timeout)
