"""Configuration helpers for the ReviewPilot app."""

from __future__ import annotations

import os
from pathlib import Path

DEFAULT_DATABASE_PATH = Path(__file__).resolve().parent.parent / "db" / "reviewpilot.db"


def get_database_path() -> Path:
    """Return the configured SQLite database path."""
    configured_path = os.getenv("REVIEWPILOT_DB_PATH")
    if configured_path:
        return Path(configured_path)
    return DEFAULT_DATABASE_PATH
