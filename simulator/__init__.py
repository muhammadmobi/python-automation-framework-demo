"""Bundled virtual MHub target under test.

The simulator is the Python equivalent of the reference Cypress demo's
``app/`` + ``mock-api/``: a self-contained system under test that ships *with*
the framework so the whole suite runs offline with zero external dependencies.
"""
from simulator.broker import InProcessBroker
from simulator.virtual_hub import VirtualHub

__all__ = ["InProcessBroker", "VirtualHub"]
