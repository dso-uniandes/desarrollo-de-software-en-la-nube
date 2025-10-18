import logging
import sys


def configure_logging(level: str | int = logging.INFO) -> None:
    """Configure root logger to print to stdout with a simple formatter.

    This ensures modules using logging.getLogger(__name__) will emit to the
    container/stdout where docker logs can capture them.
    """
    root = logging.getLogger()
    # Prevent duplicate handlers if called multiple times
    if root.handlers:
        return

    handler = logging.StreamHandler(stream=sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    root.setLevel(level)
    root.addHandler(handler)
