"""Builds an MHub :class:`HubSession` from externalised configuration.

The Python counterpart of the sibling demos' ``DriverFactory``: it reads
everything from :class:`ConfigReader` (env-overridable), wires the chosen
transport, connects the MQTT client, and registers the session with
:class:`DriverManager`. No endpoint, device id or timeout is hard-coded in a test.

In offline ("inproc") mode it also stands up the bundled virtual hub + broker so
the suite has a real target under test.
"""
from __future__ import annotations

import logging

from gateway.config import ConfigReader
from gateway.driver.driver_manager import DriverManager
from gateway.driver.mqtt_client import MqttClient
from gateway.driver.session import HubSession
from gateway.driver.transport import AwsIotTransport, InProcessTransport
from gateway.protocol.topics import resolve_topics

LOG = logging.getLogger("mhub.driver")


class DriverFactory:
    @staticmethod
    def create_driver() -> HubSession:
        transport_mode = ConfigReader.get("mhub.transport", "inproc")
        device_id = ConfigReader.get("device.id", "MHUB-DEMO-DEVICE-001")
        timeout = ConfigReader.get_int("timeout.response", 10)
        topics = resolve_topics(ConfigReader.topics(), device_id)

        hub = None
        if transport_mode == "inproc":
            transport, hub = _build_inproc(topics)
            LOG.info("Driver started against bundled virtual hub (device %s)", device_id)
        else:
            transport = _build_aws()
            LOG.info("Driver started against AWS IoT Core (device %s)", device_id)

        mqtt = MqttClient(transport, topics)
        session = HubSession(mqtt=mqtt, topics=topics, device_id=device_id, timeout=timeout, hub=hub)
        DriverManager.set_driver(session)
        return session


def _build_inproc(topics: dict):
    # Imported here so the AWS path never needs the simulator and vice versa.
    from simulator.broker import InProcessBroker
    from simulator.virtual_hub import VirtualHub

    broker = InProcessBroker()
    latency = ConfigReader.get_float("sim.latencySeconds", 0.0)
    hub = VirtualHub(broker, topics, latency=latency)
    return InProcessTransport(broker), hub


def _build_aws() -> AwsIotTransport:
    return AwsIotTransport(
        endpoint=ConfigReader.get("mqtt.endpoint"),
        port=ConfigReader.get_int("mqtt.port", 8883),
        client_id=ConfigReader.get("mqtt.clientId", "mhub-demo-"),
        root_ca=ConfigReader.get("mqtt.rootCaPath"),
        private_key=ConfigReader.get("mqtt.privateKeyPath"),
        cert=ConfigReader.get("mqtt.certPath"),
    )
