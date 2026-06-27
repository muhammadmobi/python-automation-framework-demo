"""Configuration Page Object — backlight / touch threshold / on-state level."""
from __future__ import annotations

from gateway.base import BasePage
from gateway.protocol import messages

TOPIC = "DeviceConfigure"


class ConfigurationPage(BasePage):
    def set_backlight(self, node_id: int, node_type: str, d_id: str, enabled: int) -> dict:
        return self.request(TOPIC, messages.configure_node(node_id, node_type, d_id, bl=enabled))

    def set_threshold(self, node_id: int, node_type: str, d_id: str, threshold: int) -> dict:
        return self.request(TOPIC, messages.configure_node(node_id, node_type, d_id, th=threshold))

    def set_onstate_level(self, node_id: int, node_type: str, d_id: str, level: int) -> dict:
        return self.request(TOPIC, messages.configure_node(node_id, node_type, d_id, code=None, ol=level))
