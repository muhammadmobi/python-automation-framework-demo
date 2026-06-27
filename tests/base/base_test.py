"""Base for all test classes.

Mirrors the sibling demos' ``BaseTest``: it owns the driver lifecycle and hands
tests ready-made Page Objects so a test body expresses intent only — never the
driver, topics or transport. The ``driver`` session fixture (see ``conftest.py``)
is applied automatically to every subclass.
"""
from __future__ import annotations

import logging

import pytest

from gateway.pages import AutomationPage, ConfigurationPage, NodeControlPage, ScenePage


@pytest.mark.usefixtures("driver")
class BaseTest:
    log = logging.getLogger("mhub.test")

    # ── Page Object accessors ────────────────────────────────────────────────
    def scene_page(self) -> ScenePage:
        return ScenePage()

    def control_page(self) -> NodeControlPage:
        return NodeControlPage()

    def configuration_page(self) -> ConfigurationPage:
        return ConfigurationPage()

    def automation_page(self) -> AutomationPage:
        return AutomationPage()
