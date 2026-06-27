"""Pytest fixtures + listener wiring.

Owns the driver lifecycle (the sibling demos' ``BaseTest`` ``@Before/@After``)
and registers the listener hooks. The MHub "device under test" is long-lived —
like real hardware it persists across the session — while ``_isolate`` drains
stale responses between tests so ordering quirks never leak across cases.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

import pytest

# Make the project root importable (gateway/ simulator/ tests/).
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gateway.config import ConfigReader            # noqa: E402
from gateway.driver import DriverFactory, DriverManager  # noqa: E402
from tests.data.test_data import NODE_SUFFIXES     # noqa: E402
from tests.listeners import listener               # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


# ── Driver lifecycle ─────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def driver():
    session = DriverFactory.create_driver()
    yield session
    DriverManager.quit_driver()


@pytest.fixture(autouse=True)
def _isolate(driver):
    driver.mqtt.drain()
    yield


# ── Shared data fixtures ─────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def node_ids():
    return ConfigReader.node_ids()


@pytest.fixture(scope="session")
def shadow_id():
    """Return a ``lambda node_type -> "7-4G"`` typed shadow id resolver."""
    ids = ConfigReader.node_ids()

    def _resolve(node_type: str) -> str:
        return f"{ids[node_type]}{NODE_SUFFIXES[node_type]}"

    return _resolve


# ── Listener hooks (delegated to tests/listeners/listener.py) ─────────────────
def pytest_runtest_logstart(nodeid, location):
    listener.on_start(nodeid)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    listener.on_report(outcome.get_result())
