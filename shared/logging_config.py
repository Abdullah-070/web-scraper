"""
Centralized logging configuration 
"""

from __future__ import annotations

import logging
import os
import sys

LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | job_id=%(job_id)s | %(message)s"
)
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()


class _JobIdFilter(logging.Filter):
    """Ensures every log record has a `job_id` attribute
    """

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "job_id"):
            record.job_id = "-"
        return True


def configure_logging() -> None:
    """Call this once, at process start 
    """
    root_logger = logging.getLogger("sdip")
    if root_logger.handlers:
        return  # already configured

    root_logger.setLevel(LOG_LEVEL)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    handler.addFilter(_JobIdFilter())

    root_logger.addHandler(handler)
    root_logger.propagate = False


def get_job_logger(name: str, job_id: str | None = None) -> logging.LoggerAdapter:
    """Return a logger that automatically stamps every message with the
    given job_id
    """
    base_logger = logging.getLogger(name)
    return logging.LoggerAdapter(base_logger, {"job_id": job_id or "-"})
