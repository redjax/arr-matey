from dataclasses import dataclass
import logging
import logging.handlers
import sys
from pathlib import Path

from dotenv import dotenv_values

__all__ = ["REPO_ROOT", "Config", "get_config", "setup_logging"]

REPO_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = REPO_ROOT / ".env"


@dataclass(frozen=True)
class Config:
    """Config class to store settings loaded from environment variables/.env file."""

    media_root: Path
    config_root: Path

    log_level: str
    log_file: Path

    domain: str

    ntfy_server: str
    ntfy_topic: str


def get_config() -> Config:
    """Return an object with app configuration loaded from the environment."""
    env: dict[str, str | None] = dotenv_values(ENV_PATH)

    config_root: Path = Path(env["CONFIG_ROOT"])

    log_file = Path(env.get("LOG_FILE", "logs/stack.log"))
    # Ensure log_file has a drive/mount prefix (/path/to/log or D:\\path\\to\\log)
    if not log_file.is_absolute():
        log_file = config_root / log_file

    return Config(
        media_root=Path(env["MEDIA_ROOT"]),
        config_root=config_root,
        log_level=env.get("LOG_LEVEL", "INFO").upper(),
        log_file=log_file,
        domain=env.get("DOMAIN", ""),
        ntfy_server=env.get("NTFY_SERVER", "https://ntfy.sh"),
        ntfy_topic=env.get("NTFY_TOPIC", ""),
    )


def setup_logging(config: Config):
    """Setup Python logging module.

    Call this function once in your script's entrypoint, then set
    a logger for the module with log = logging.getLogger(__name__).
    """
    # Ensure log file parent directories exist
    config.log_file.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=config.log_level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            # Log file handler
            logging.handlers.RotatingFileHandler(
                config.log_file,
                # Max size=10MB
                maxBytes=10_000_000,
                backupCount=2,
                encoding="utf-8",
            ),
            logging.StreamHandler(sys.stdout),
        ],
    )
