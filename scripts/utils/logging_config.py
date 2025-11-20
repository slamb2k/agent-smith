"""Logging configuration for Agent Smith."""

import logging
import sys
from pathlib import Path
from typing import Optional


# Global flag to track if logging has been configured
_logging_configured = False


def setup_logging(
    log_dir: Optional[Path] = None,
    log_level: str = "INFO",
    log_to_console: bool = True,
    log_to_file: bool = True,
    force: bool = False,
) -> None:
    """Configure logging for Agent Smith.

    Sets up:
    - Console logging with colored output
    - File logging to rotating log files
    - Separate error log file
    - Structured log format

    Args:
        log_dir: Directory for log files (default: ./logs)
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR)
        log_to_console: Whether to log to console
        log_to_file: Whether to log to files
        force: Force reconfiguration even if already configured
    """
    global _logging_configured

    if _logging_configured and not force:
        return

    if log_dir is None:
        project_root = Path(__file__).parent.parent.parent
        log_dir = project_root / "logs"

    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    # Get numeric log level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Create formatters
    console_formatter = logging.Formatter("%(levelname)-8s | %(name)-20s | %(message)s")

    file_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

    # File handlers
    if log_to_file:
        # Main log file
        log_file = log_dir / "operations.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

        # Error log file
        error_file = log_dir / "errors.log"
        error_handler = logging.FileHandler(error_file)
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        root_logger.addHandler(error_handler)

        # API calls log file
        api_file = log_dir / "api_calls.log"
        api_handler = logging.FileHandler(api_file)
        api_handler.setLevel(logging.DEBUG)
        api_handler.setFormatter(file_formatter)

        # Add filter to only log API-related messages
        api_handler.addFilter(lambda record: "api" in record.name.lower())
        root_logger.addHandler(api_handler)

    _logging_configured = True

    root_logger.info(f"Logging configured (level: {log_level}, dir: {log_dir})")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def reset_logging() -> None:
    """Reset logging configuration (useful for testing)."""
    global _logging_configured
    _logging_configured = False
    logging.getLogger().handlers.clear()
