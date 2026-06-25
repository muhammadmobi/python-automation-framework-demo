"""Loads framework configuration from ``resources/config.properties``.

The Python counterpart of the sibling demos' ``ConfigReader``: a single, static
entry point for externalised configuration. An environment variable always takes
precedence over the properties file — the equivalent of Appium's
``-Dkey=value`` overrides — so nothing (device id, endpoint, timeouts) is ever
hard-coded in a test.

The MHub protocol data (topics / node ids / command codes) lives alongside in
``resources/config.json`` and is exposed through :meth:`protocol`.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict

RESOURCES = Path(__file__).resolve().parents[2] / "resources"
PROPERTIES_FILE = RESOURCES / "config.properties"
PROTOCOL_FILE = RESOURCES / "config.json"


def _env_key(key: str) -> str:
    return key.upper().replace(".", "_")


class ConfigReader:
    """Static configuration accessor (env var > properties file > default)."""

    _properties: Dict[str, str] = {}
    _protocol: dict = {}

    @classmethod
    def _load(cls) -> None:
        if cls._properties:
            return
        if not PROPERTIES_FILE.exists():
            raise FileNotFoundError(f"config.properties not found at {PROPERTIES_FILE}")
        for raw in PROPERTIES_FILE.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            cls._properties[key.strip()] = value.strip()
        with PROTOCOL_FILE.open("r", encoding="utf-8") as handle:
            cls._protocol = json.load(handle)

    @classmethod
    def get(cls, key: str, default: str | None = None) -> str | None:
        cls._load()
        env = os.getenv(_env_key(key))
        if env is not None and env != "":
            return env
        value = cls._properties.get(key)
        return value if (value is not None and value != "") else default

    @classmethod
    def get_int(cls, key: str, default: int) -> int:
        value = cls.get(key)
        return int(value) if value is not None else default

    @classmethod
    def get_float(cls, key: str, default: float) -> float:
        value = cls.get(key)
        return float(value) if value is not None else default

    # ── protocol (config.json) ───────────────────────────────────────────────
    @classmethod
    def protocol(cls) -> dict:
        cls._load()
        return cls._protocol

    @classmethod
    def topics(cls) -> dict:
        return cls.protocol()["topics"]

    @classmethod
    def node_ids(cls) -> dict:
        return cls.protocol()["node_ids"]

    @classmethod
    def command(cls, name: str) -> int:
        return cls.protocol()["command"][name]
