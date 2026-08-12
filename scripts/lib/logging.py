import logging

from .config import Config

__all__ = [
    "setup_logging",
]


def setup_logging(config: Config) -> None:
    """Configure Python logging module.

    Call this function early in your script's execution, i.e.
    directly after initializing the app's Config object.
    """
    # Ensure log file's parent directories exist
    config.log_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    logging.basicConfig(
        level=getattr(logging, config.log_level.upper()),
        format=config.log_format,
        datefmt=config.log_datefmt,
        filename=config.log_file,
    )
