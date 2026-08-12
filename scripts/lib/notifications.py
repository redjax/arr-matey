import requests

from .config import Config

__all__ = [
    "notify_ntfy",
]


def notify_ntfy(
    config: Config,
    message: str,
    *,
    title: str | None = None,
) -> None:
    if not config.ntfy_url or not config.ntfy_topic:
        return

    url = f"{config.ntfy_url.rstrip('/')}" f"/{config.ntfy_topic}"

    headers = {}

    if title:
        headers["Title"] = title

    response = requests.post(
        url,
        data=message.encode("utf-8"),
        headers=headers,
        timeout=30,
    )

    response.raise_for_status()
