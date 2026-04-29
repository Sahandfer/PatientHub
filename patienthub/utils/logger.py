from __future__ import annotations

import logging
from enum import StrEnum
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler

console = Console()
err_console = Console(stderr=True)


class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


def setup_logging(
    level: LogLevel = LogLevel.INFO, log_file: Path | None = None
) -> None:
    """Configure rich console logging, and optionally file logging."""
    log_level = getattr(logging, level.value)

    root = logging.getLogger()
    root.setLevel(log_level)

    rich_handler = RichHandler(
        level=log_level,
        console=Console(stderr=True),
        show_time=True,
        show_path=False,
        markup=True,
        rich_tracebacks=True,
        tracebacks_show_locals=level == LogLevel.DEBUG,
    )
    rich_handler.setFormatter(logging.Formatter("%(message)s"))
    root.addHandler(rich_handler)

    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(log_file)
        fh.setLevel(log_level)
        fh.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        )
        root.addHandler(fh)


def init_logging(
    name: str, level: LogLevel = LogLevel.INFO, log_dir: Path = Path("logs")
) -> Path:
    """Clear existing handlers, configure logging, and return the log file path."""
    from datetime import datetime

    log_file = log_dir / f"{name}_{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
    logging.root.handlers.clear()
    setup_logging(level, log_file=log_file)
    return log_file


def get_logger(name: str) -> logging.Logger:
    """Get a named logger. Call init_logging() once at app entry point."""
    return logging.getLogger(name)
