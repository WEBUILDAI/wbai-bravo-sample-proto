"""Einheitliches Logging-Setup nach WBAI-Standard."""

import logging
import os

_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


def setup_logging(level: str | None = None) -> None:
    """Konfiguriert das Root-Logging einmalig.

    Args:
        level: Log-Level als Name (z.B. "INFO"). Fällt auf die Umgebungsvariable
            LOG_LEVEL und danach auf "INFO" zurück.

    """
    logging.basicConfig(
        level=(level or os.getenv("LOG_LEVEL", "INFO")).upper(),
        format=_FORMAT,
    )
