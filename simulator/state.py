"""In-memory device state for the virtual hub.

Holds the things a real MasterHub keeps track of: which scenes and automations
exist, the last-applied switch state of every node, and per-node device
configuration (backlight / touch threshold / on-state level). Keeping real
state lets the handlers return *meaningful* return codes — e.g. running or
deleting a scene that was never created fails, exactly as on hardware.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class NodeConfig:
    backlight: int = 1
    threshold: int = 25
    onstate_level: int = 100


@dataclass
class HubState:
    scenes: Dict[int, dict] = field(default_factory=dict)
    automations: Dict[int, dict] = field(default_factory=dict)
    node_switch: Dict[str, List[int]] = field(default_factory=dict)
    node_config: Dict[str, NodeConfig] = field(default_factory=dict)
    detected: List[dict] = field(default_factory=list)

    def config_for(self, node_id: str) -> NodeConfig:
        return self.node_config.setdefault(node_id, NodeConfig())
