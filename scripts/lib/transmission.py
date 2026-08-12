import requests

from .config import Config

__all__ = [
    "transmission_request",
]


def transmission_request(
    config: Config,
    method: str,
    params: list | None = None,
) -> dict:
    """Send RPC request to Transmission client."""
    if not config.transmission_url:
        raise ValueError("TRANSMISSION_URL is not configured")

    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params or [],
        "id": 1,
    }

    auth = None

    if config.transmission_username:
        auth = (
            config.transmission_username,
            config.transmission_password or "",
        )

    response = requests.post(
        config.transmission_url,
        json=payload,
        auth=auth,
        timeout=30,
    )

    response.raise_for_status()

    result = response.json()

    if result.get("error"):
        raise RuntimeError(result["error"])

    return result["result"]
