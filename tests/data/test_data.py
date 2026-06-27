"""Centralised data providers — the pytest analogue of TestNG's ``TestData``.

Each provider returns ``(parametrize_argvalues, ids)`` so a spec can write::

    values, ids = TestData.scene_lifecycle()
    @pytest.mark.parametrize("test_id, node_type, group, scene_id, s_value", values, ids=ids)
"""
from __future__ import annotations

# Node-type -> shadow-id suffix (the control plane addresses nodes by typed id).
NODE_SUFFIXES = {"4g": "-4G", "3g": "-3G", "2g": "-2G", "1g": "-1G",
                 "fd": "-FD", "pp": "-PP", "sr": "-SR", "sp": "-SP"}

# DbId config keys per node type (device configuration domain).
DB_ID_KEYS = {"4g": "4GDbId", "3g": "3GDbId", "2g": "2GDbId",
              "1g": "1GDbId", "fd": "FdDbId", "pp": "PpDbId"}


class TestData:
    # ── Scene ────────────────────────────────────────────────────────────────
    _SCENE_LIFECYCLE = [
        ("MHUB-SCENE-4G-01", "4g", "TP", 101, 1),
        ("MHUB-SCENE-4G-02", "4g", "TP", 102, 166),
        ("MHUB-SCENE-4G-03", "4g", "TP", 103, 16),
        ("MHUB-SCENE-4G-04", "4g", "TP", 104, 64),
        ("MHUB-SCENE-3G-01", "3g", "TP", 501, 41),
        ("MHUB-SCENE-3G-02", "3g", "TP", 502, 38),
        ("MHUB-SCENE-2G-01", "2g", "TP", 201, 9),
        ("MHUB-SCENE-1G-01", "1g", "TP", 301, 1),
        ("MHUB-SCENE-PP-01", "pp", "PP", 401, 1),
        ("MHUB-SCENE-SR-01", "sr", "TP", 701, 9),
        ("MHUB-SCENE-SP-01", "sp", "TP", 801, 1),
    ]

    @classmethod
    def scene_lifecycle(cls):
        return cls._SCENE_LIFECYCLE, [row[0] for row in cls._SCENE_LIFECYCLE]

    # ── Node control (shadow) ────────────────────────────────────────────────
    _TURN_ON = [
        ("MHUB-CTRL-4G-ON", "4g", [0, 1], 1),
        ("MHUB-CTRL-3G-ON", "3g", [1, 2], 2),
        ("MHUB-CTRL-2G-ON", "2g", [2, 4], 4),
        ("MHUB-CTRL-1G-ON", "1g", [0, 1], 1),
        ("MHUB-CTRL-FD-ON", "fd", [6, 1], 1),
        ("MHUB-CTRL-PP-ON", "pp", [0, 1], 1),
        ("MHUB-CTRL-SR-ON", "sr", [1, 2], 2),
    ]
    _TURN_OFF = [
        ("MHUB-CTRL-4G-OFF", "4g", [255, 0], 0),
        ("MHUB-CTRL-FD-OFF", "fd", [6, 0], 0),
        ("MHUB-CTRL-1G-OFF", "1g", [0, 0], 0),
    ]

    @classmethod
    def turn_on(cls):
        return cls._TURN_ON, [row[0] for row in cls._TURN_ON]

    @classmethod
    def turn_off(cls):
        return cls._TURN_OFF, [row[0] for row in cls._TURN_OFF]

    # ── Device configuration ─────────────────────────────────────────────────
    _BACKLIGHT = [("4g", "4G"), ("3g", "3G"), ("2g", "2G"), ("1g", "1G"), ("fd", "FD"), ("pp", "PP")]
    _THRESHOLDS = [("1g", "1G", 15), ("2g", "2G", 25), ("3g", "3G", 32),
                   ("4g", "4G", 12), ("fd", "FD", 18), ("pp", "PP", 20)]
    _ONSTATE_LEVELS = [0, 10, 40, 70, 100]

    @classmethod
    def backlight(cls):
        return cls._BACKLIGHT, [row[1] for row in cls._BACKLIGHT]

    @classmethod
    def thresholds(cls):
        return cls._THRESHOLDS, [f"{r[1]}-{r[2]}" for r in cls._THRESHOLDS]

    @classmethod
    def onstate_levels(cls):
        return cls._ONSTATE_LEVELS

    # ── Automation device map ────────────────────────────────────────────────
    @staticmethod
    def all_node_devices(node_ids: dict) -> dict:
        return {
            "FD": [{"id": node_ids["fd"], "s": [6, 1]}],
            "TP": [
                {"id": node_ids["1g"], "s": 1},
                {"id": node_ids["2g"], "s": 5},
                {"id": node_ids["3g"], "s": 21},
                {"id": node_ids["4g"], "s": 85},
            ],
            "SR": [{"id": node_ids["sr"], "s": 5}],
            "PP": [{"id": node_ids["pp"], "s": 1}],
        }
