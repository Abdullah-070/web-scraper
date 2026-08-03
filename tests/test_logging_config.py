"""
Tests for shared.logging_config 
"""

import logging

from shared.logging_config import configure_logging, get_job_logger


def test_configure_logging_is_idempotent():
    """Calling configure_logging() multiple times must not duplicate
    handlers
    """
    configure_logging()
    handler_count_after_first = len(logging.getLogger("sdip").handlers)

    configure_logging()
    handler_count_after_second = len(logging.getLogger("sdip").handlers)

    assert handler_count_after_first == handler_count_after_second
    assert handler_count_after_first >= 1


def test_get_job_logger_stamps_job_id(caplog):
    configure_logging()
    job_logger = get_job_logger("sdip.test", job_id="abc-123")

    with caplog.at_level(logging.INFO):
        job_logger.info("hello from a test")

    assert any("abc-123" in record.job_id for record in caplog.records if hasattr(record, "job_id"))


def test_get_job_logger_defaults_job_id_placeholder_when_none():
    job_logger = get_job_logger("sdip.test", job_id=None)
    # LoggerAdapter stores extra in .extra
    assert job_logger.extra["job_id"] == "-"
