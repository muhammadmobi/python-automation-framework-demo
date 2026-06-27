"""Node Control Page Object — direct shadow control + device detect."""
from __future__ import annotations

from gateway.base import BasePage
from gateway.protocol import messages


class NodeControlPage(BasePage):
    def set_switch(self, node_id: str, s_value) -> dict:
        """Publish a desired shadow update and return the reported state."""
        return self.request("ShadowUpdate", messages.shadow_update(node_id, s_value))

    def detect(self, node_id: int, node_type: str) -> None:
        """Fire-and-forget device detect (no response expected)."""
        self.publish("DetectDevice", messages.detect_device(node_id, node_type))
