"""Automation Page Object — time-window Create / Edit / Delete."""
from __future__ import annotations

from gateway.base import BasePage
from gateway.protocol import messages

TOPIC = "Automation"


class AutomationPage(BasePage):
    def create(self, aid: int, sid: int, devices: dict, duration_min: int = 5) -> dict:
        return self.request(TOPIC, messages.create_automation(aid, sid, devices, duration_min=duration_min))

    def edit(self, aid: int, sid: int, *, add=None, edit=None) -> dict:
        return self.request(TOPIC, messages.edit_automation(aid, sid, add=add, edit=edit))

    def delete(self, aid: int, sid: int) -> dict:
        return self.request(TOPIC, messages.delete_automation(aid, sid))
