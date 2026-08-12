from urllib.parse import urlparse

import requests

from .config import Config

__all__ = [
    "parse_seedbox_host",
    "seedbox_request",
]


def parse_seedbox_host(
    url: str,
) -> tuple[str, int | None]:
    """Parse seedbox hostname from a given URL."""
    parsed = urlparse(url)

    if not parsed.hostname:
        raise ValueError(f"Invalid seedbox URL: {url}")

    return parsed.hostname, parsed.port


def seedbox_request(
    config: Config,
    method: str,
    path: str,
    **kwargs,
) -> requests.Response:
    """Send HTTP request to seedbox."""
    if not config.seedbox_url:
        raise ValueError("SEEDBOX_URL is not configured")

    url = f"{config.seedbox_url.rstrip('/')}" f"/{path.lstrip('/')}"

    auth = None

    if config.seedbox_username:
        auth = (
            config.seedbox_username,
            config.seedbox_password or "",
        )

    response = requests.request(
        method,
        url,
        auth=auth,
        timeout=30,
        **kwargs,
    )

    response.raise_for_status()

    return response
