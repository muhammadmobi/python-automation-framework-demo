"""Pluggable MQTT transports — the driver's lowest layer.

One ``Transport`` interface over *either* the bundled in-process broker (offline,
default) or a real AWS IoT Core endpoint. This is the seam that lets the same
Page Objects and tests run against the virtual hub or real hardware unchanged.
"""
from __future__ import annotations

import os
import uuid
from typing import Callable, Protocol

from simulator.broker import InProcessBroker

Callback = Callable[[str, bytes], None]


class Transport(Protocol):
    def publish(self, topic: str, payload: bytes) -> None: ...
    def subscribe(self, topic: str, callback: Callback) -> None: ...
    def disconnect(self) -> None: ...


class InProcessTransport:
    """Wraps the bundled broker so the client speaks to the virtual hub."""

    def __init__(self, broker: InProcessBroker) -> None:
        self._broker = broker

    def publish(self, topic: str, payload: bytes) -> None:
        self._broker.publish(topic, payload)

    def subscribe(self, topic: str, callback: Callback) -> None:
        self._broker.subscribe(topic, callback)

    def disconnect(self) -> None:
        return None


class AwsIotTransport:
    """Real AWS IoT Core transport (parity path; not used in offline CI).

    Imports ``AWSIoTPythonSDK`` lazily so the offline suite has zero AWS deps.
    """

    def __init__(self, *, endpoint: str, port: int, client_id: str,
                 root_ca: str, private_key: str, cert: str) -> None:
        from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient  # noqa: WPS433

        root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        client = AWSIoTMQTTClient(client_id + str(uuid.uuid4()))
        client.configureEndpoint(endpoint, port)
        client.configureCredentials(
            os.path.join(root, root_ca),
            os.path.join(root, private_key),
            os.path.join(root, cert),
        )
        client.configureConnectDisconnectTimeout(10)
        client.configureMQTTOperationTimeout(5)
        client.connect()
        self._client = client

    def publish(self, topic: str, payload: bytes) -> None:
        self._client.publish(topic, payload.decode("utf-8"), 1)

    def subscribe(self, topic: str, callback: Callback) -> None:
        self._client.subscribe(topic, 1, lambda c, u, m: callback(m.topic, m.payload))

    def disconnect(self) -> None:
        self._client.disconnect()
