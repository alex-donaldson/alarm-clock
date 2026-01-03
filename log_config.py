"""Shared logging configuration helper.

Provides get_logger(name, filename=None, level=logging.INFO, max_bytes=5_242_880, backup_count=3)
which returns a logger configured with a RotatingFileHandler writing to logs/<filename> (or logs/<name>.log if filename omitted).
Ensures the logs directory exists and avoids adding duplicate handlers when called multiple times.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = "logs"


def get_logger(name: str, filename: str = None, level: int = logging.INFO, max_bytes: int = 5_242_880, backup_count: int = 3):
    """Return a configured logger.

    Args:
        name: logger name
        filename: base filename (without path) to write logs to; if None uses "{name}.log".
        level: logging level
        max_bytes: max bytes before rotation
        backup_count: number of rotated files to keep

    Returns:
        logging.Logger
    """
    if not os.path.exists(LOG_DIR):
        try:
            os.makedirs(LOG_DIR, exist_ok=True)
        except Exception:
            # If cannot create, fallback to current directory
            pass

    if filename:
        logfile = os.path.join(LOG_DIR, filename)
    else:
        logfile = os.path.join(LOG_DIR, f"{name}.log")

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding duplicate handlers if logger already configured
    if not any(isinstance(h, RotatingFileHandler) and getattr(h, 'baseFilename', None) == os.path.abspath(logfile) for h in logger.handlers):
        # Rotating file handler
        fh = RotatingFileHandler(logfile, maxBytes=max_bytes, backupCount=backup_count)
        fh.setLevel(level)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    # Ensure there is at least one stream handler for console output if none
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s'))
        logger.addHandler(ch)

    return logger
