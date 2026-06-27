"""Scene Page Object — Create / Run / Edit / Delete scenes."""
from __future__ import annotations

from gateway.base import BasePage
from gateway.protocol import messages

TOPIC = "scene"


class ScenePage(BasePage):
    def create(self, sid: int, group: str, node_id, s_value) -> dict:
        return self.request(TOPIC, messages.create_scene(sid, group, node_id, s_value))

    def run(self, sid: int) -> dict:
        return self.request(TOPIC, messages.run_scene(sid))

    def delete(self, sid: int) -> dict:
        return self.request(TOPIC, messages.delete_scene(sid))

    def edit(self, sid: int, *, edit=None, add=None, delete=None) -> dict:
        return self.request(TOPIC, messages.edit_scene(sid, edit=edit, add=add, delete=delete))
