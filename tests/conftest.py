"""Test configuration helpers for local imports."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

provider_router = importlib.import_module("app.provider_router")


@pytest.fixture(autouse=True)
def _reset_provider_router_state() -> None:
    """Reset provider router cooldown state before and after each test."""
    provider_router.clear_router_state()
    yield
    provider_router.clear_router_state()
