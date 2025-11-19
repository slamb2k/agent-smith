"""Tests for logging configuration."""
import logging
import tempfile
from pathlib import Path
import pytest
from scripts.utils.logging_config import setup_logging, get_logger, reset_logging


@pytest.fixture(autouse=True)
def reset_logging_after_test():
    """Reset logging configuration after each test."""
    yield
    reset_logging()


def test_setup_logging_creates_log_directory():
    """Test that setup_logging creates log directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        log_dir = Path(temp_dir) / "logs"
        setup_logging(log_dir=log_dir)
        assert log_dir.exists()


def test_setup_logging_configures_root_logger():
    """Test that setup_logging configures root logger."""
    with tempfile.TemporaryDirectory() as temp_dir:
        log_dir = Path(temp_dir) / "logs"
        setup_logging(log_dir=log_dir, log_level="DEBUG")

        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG


def test_get_logger_returns_configured_logger():
    """Test get_logger returns properly configured logger."""
    logger = get_logger("test_module")
    assert logger.name == "test_module"
    assert isinstance(logger, logging.Logger)


def test_logging_writes_to_file():
    """Test that logs are written to file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        log_dir = Path(temp_dir) / "logs"
        setup_logging(log_dir=log_dir)

        logger = get_logger("test")
        logger.info("Test message")

        # Check log file was created
        log_files = list(log_dir.glob("*.log"))
        assert len(log_files) > 0
