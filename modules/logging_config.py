"""
Logging configuration for Frida Freq

Usage in main.py or other modules:

    from modules.logging_config import setup_logging

    # Initialize logging (do this once in main.py)
    logger = setup_logging(log_level="INFO")

    # Use the logger
    logger.info("Your message here")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.debug("Debug message")

Advanced usage:

    # Custom log level
    logger = setup_logging(log_level="DEBUG")

    # Custom log file path
    logger = setup_logging(log_file="custom/path/app.log")

    # Console logging only (no file)
    logger = setup_logging(log_file=None)

    # Get logger in other modules (after setup_logging was called)
    import logging
    logger = logging.getLogger('frida_freq')
"""
import logging
import sys
from pathlib import Path


def setup_logging(log_level: str = "INFO", log_file: str = "logs/frida-freq.log"):
    """
    Configure logging for the application

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file. If None, only logs to stdout
    """
    handlers = [logging.StreamHandler(sys.stdout)]

    # Add file handler if log_file is specified
    if log_file:
        # Create log directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

    # Return a logger for the main application
    return logging.getLogger('frida_freq')