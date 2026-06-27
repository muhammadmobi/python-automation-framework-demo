"""Test listener — structured pass/fail logging and a failure artifact.

The pytest analogue of the sibling demos' ``TestListener``. A UI listener
attaches a screenshot on failure; with no UI, the equivalent diagnostic here is a
dump of the virtual hub's in-memory state (scenes / automations / node switches /
config) at the moment of failure, which is what you would inspect to debug.

The hooks are wired into pytest from ``conftest.py``.
"""
from __future__ import annotations

import logging

from gateway.driver.driver_manager import DriverManager

LOG = logging.getLogger("mhub.listener")


def on_start(test_name: str) -> None:
    LOG.info("[START] %s", test_name)


def on_report(report) -> None:
    if report.when != "call":
        return
    if report.passed:
        LOG.info("[PASS]  %s", report.nodeid)
    elif report.failed:
        LOG.error("[FAIL]  %s", report.nodeid)
        _dump_hub_state()
    elif report.skipped:
        LOG.warning("[SKIP]  %s", report.nodeid)


def _dump_hub_state() -> None:
    """Attach the virtual hub's state on failure (offline target only)."""
    try:
        session = DriverManager.get_driver()
        hub = getattr(session, "hub", None)
        if hub is None:
            return
        state = hub.state
        LOG.error(
            "[HUB STATE] scenes=%s automations=%s switches=%s",
            sorted(state.scenes), sorted(state.automations), state.node_switch,
        )
    except Exception as exc:  # diagnostics must never mask the real failure
        LOG.warning("Could not capture hub state: %s", exc)
