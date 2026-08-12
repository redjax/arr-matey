from dataclasses import dataclass
import os
from pathlib import Path

__all__ = [
    "ApiConfig",
    "Config",
    "get_config",
]


@dataclass(frozen=True)
class ApiConfig:
    """Generic API configuration."""

    url: str
    api_key: str


@dataclass(frozen=True)
class Config:
    """App config object.

    Populate with values loaded from the environment. Run get_config()
    in a script to initialize the object, then re-use it throughout
    the script to get values during runtime.
    """

    config_root: Path

    log_level: str
    log_file: Path
    log_format: str
    log_datefmt: str

    sonarr: ApiConfig | None
    radarr: ApiConfig | None

    transmission_url: str | None
    transmission_username: str | None
    transmission_password: str | None

    seedbox_url: str | None
    seedbox_username: str | None
    seedbox_password: str | None

    ntfy_url: str | None
    ntfy_topic: str | None


def _api_config(prefix: str) -> ApiConfig | None:
    """Return initialized ApiConfig class."""
    url = os.environ.get(f"{prefix}_URL")
    api_key = os.environ.get(f"{prefix}_API_KEY")

    if not url:
        return None

    if not api_key:
        raise ValueError(f"{prefix}_API_KEY is required")

    return ApiConfig(
        url=url.rstrip("/"),
        api_key=api_key,
    )


def get_config() -> Config:
    """Return initialized Config class."""
    config_root = Path(os.environ.get("CONFIG_ROOT", "."))

    return Config(
        config_root=config_root,
        log_level=os.environ.get("LOG_LEVEL", "INFO"),
        log_file=config_root
        / os.environ.get(
            "LOG_FILE",
            "logs/stack.log",
        ),
        log_format=os.environ.get(
            "LOG_FORMAT",
            "%(asctime)s %(levelname)s %(name)s: %(message)s",
        ),
        log_datefmt=os.environ.get(
            "LOG_DATEFMT",
            "%Y-%m-%d %H:%M:%S",
        ),
        sonarr=_api_config("SONARR"),
        radarr=_api_config("RADARR"),
        transmission_url=os.environ.get("TRANSMISSION_URL"),
        transmission_username=os.environ.get("TRANSMISSION_USERNAME"),
        transmission_password=os.environ.get("TRANSMISSION_PASSWORD"),
        seedbox_url=os.environ.get("SEEDBOX_URL"),
        seedbox_username=os.environ.get("SEEDBOX_USERNAME"),
        seedbox_password=os.environ.get("SEEDBOX_PASSWORD"),
        ntfy_url=os.environ.get("NTFY_URL"),
        ntfy_topic=os.environ.get("NTFY_TOPIC"),
    )
