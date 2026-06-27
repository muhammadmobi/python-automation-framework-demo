"""Thread-safe holder for the MHub :class:`HubSession`.

Mirrors the sibling demos' ``DriverManager``: a ``threading.local`` keeps one
session per test thread, so suites can run in parallel without sharing state.
"""
from __future__ import annotations

import threading

from gateway.driver.session import HubSession

_LOCAL = threading.local()


class DriverManager:
    @staticmethod
    def get_driver() -> HubSession:
        session = getattr(_LOCAL, "session", None)
        if session is None:
            raise RuntimeError("Driver has not been initialised for this thread")
        return session

    @staticmethod
    def set_driver(session: HubSession) -> None:
        _LOCAL.session = session

    @staticmethod
    def quit_driver() -> None:
        session = getattr(_LOCAL, "session", None)
        if session is not None:
            session.quit()
            _LOCAL.session = None
