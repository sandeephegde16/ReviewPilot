"""Logging configuration for ReviewPilot application telemetry."""

from __future__ import annotations

import logging
import sys

_LOGGER_NAME = "reviewpilot"
_LOGGING_CONFIGURED = False


def configure_logging(*, force: bool = False) -> None:
    """Configure structured telemetry logging to stdout."""
    global _LOGGING_CONFIGURED
    if _LOGGING_CONFIGURED and not force:
        return

    logger = logging.getLogger(_LOGGER_NAME)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter("%(message)s"))

    logger.addHandler(handler)
    logger.propagate = False
    _LOGGING_CONFIGURED = True
