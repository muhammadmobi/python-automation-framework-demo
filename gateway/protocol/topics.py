"""Topic resolution — substitutes the device id into the topic templates.

The MQTT analogue of the sibling demos' isolated *locator* layer: a topic-scheme
change touches exactly one place.
"""
from __future__ import annotations

import json


def resolve_topics(topics_template: dict, device_id: str) -> dict:
    """Return a copy of ``topics_template`` with ``{id}`` replaced everywhere."""
    if not device_id:
        raise ValueError("device_id is required to resolve MQTT topics")
    return json.loads(json.dumps(topics_template).replace("{id}", device_id))
