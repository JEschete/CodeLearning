"""
Central logging configuration for AntennaForge.

Usage in any module:
    import logging
    logger = logging.getLogger(__name__)
    logger.info("message")

Call ``setup_logging()`` once at startup (in cli.py / __main__.py)
to configure format, level, and optional file output.
"""

import logging
import os
import sys

_CONFIGURED = False

DEFAULT_FORMAT = "%(levelname)-8s %(name)-30s  %(message)s"
VERBOSE_FORMAT = ("%(asctime)s  %(levelname)-8s  "
                  "%(name)-30s  %(message)s")


def setup_logging(level=logging.INFO,
                  log_file=None,
                  verbose=False):
    """Initialise the root logger for AntennaForge.

    Args:
        level:    logging level (DEBUG, INFO, WARNING …)
        log_file: optional path to a log file
        verbose:  if True, use timestamped format
    """
    global _CONFIGURED
    if _CONFIGURED:
        return
    _CONFIGURED = True

    fmt = VERBOSE_FORMAT if verbose else DEFAULT_FORMAT
    formatter = logging.Formatter(fmt)

    root = logging.getLogger()
    root.setLevel(level)

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    ch.setFormatter(formatter)
    root.addHandler(ch)

    # Optional file handler
    if log_file:
        os.makedirs(os.path.dirname(log_file) or ".",
                     exist_ok=True)
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter(VERBOSE_FORMAT))
        root.addHandler(fh)

    # Suppress noisy third-party loggers
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
