"""Central logging configuration helper.

Call configure_logging() from CLI or demos to enable console logging. Tests and
import-time behavior won't be changed unless configure_logging is called.
"""
import logging
from typing import Optional


def configure_logging(level: int = logging.INFO, handler: Optional[logging.Handler] = None) -> None:
    """Configure root logger if it has no handlers yet.

    This avoids adding duplicate handlers when tests or other frameworks
    already configure logging.
    """
    root = logging.getLogger()
    if not root.handlers:
        if handler is None:
            handler = logging.StreamHandler()
        fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        handler.setFormatter(fmt)
        root.addHandler(handler)
    root.setLevel(level)
