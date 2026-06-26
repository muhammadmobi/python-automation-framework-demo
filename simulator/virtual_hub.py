"""The virtual MasterHub.

Subscribes to the topics the cloud/app publishes *to* the device, routes each
message to the right domain handler, and publishes the handler's response on the
matching ``cloud``/``shadow accepted`` topic — exactly the wiring a real hub
performs against AWS IoT Core, but in-process and deterministic.
"""
from __future__ import annotations

import json
import time

from simulator.broker import InProcessBroker
from simulator.state import HubState
from simulator.handlers import scene, shadow, config, automation, detect


class VirtualHub:
    def __init__(self, broker: InProcessBroker, topics: dict, latency: float = 0.0) -> None:
        self._broker = broker
        self._topics = topics
        self._latency = latency
        self.state = HubState()

        pub = topics["publish"]
        sub = topics["subscription"]

        # Map an inbound (device-bound) topic to its handler and response topic.
        self._routes = {
            pub["scene"]: (self._wrap(scene.handle), sub["scene"]),
            pub["ShadowUpdate"]: (self._wrap(shadow.handle), sub["ShadowAccepted"]),
            pub["DeviceConfigure"]: (self._wrap(config.handle), sub["DeviceConfigure"]),
            pub["Automation"]: (self._wrap(automation.handle), sub["Automation"]),
            pub["DetectDevice"]: (self._wrap(detect.handle), None),
        }

        for inbound_topic in self._routes:
            broker.subscribe(inbound_topic, self._on_message)

    def _wrap(self, handler):
        return lambda msg: handler(self.state, msg)

    def _on_message(self, topic: str, payload: bytes) -> None:
        handler, response_topic = self._routes[topic]
        message = json.loads(payload.decode("utf-8"))
        response = handler(message)
        if response is None or response_topic is None:
            return
        if self._latency:
            time.sleep(self._latency)
        self._broker.publish(
            response_topic, json.dumps(response, separators=(",", ":")).encode("utf-8")
        )
