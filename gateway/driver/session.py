"""The MHub "driver" handle held by :class:`DriverManager`.

For a UI framework the driver is a WebDriver/AndroidDriver. Here the equivalent
session is the connected MQTT client plus the resolved topic map, the response
timeout, and — in offline mode — a handle to the bundled virtual hub (so tests
can assert against its in-memory state).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from gateway.driver.mqtt_client import MqttClient


@dataclass
class HubSession:
    mqtt: MqttClient
    topics: dict
    device_id: str
    timeout: int
    hub: Optional[object] = None  # simulator.VirtualHub when transport == inproc

    def quit(self) -> None:
        self.mqtt.disconnect()
