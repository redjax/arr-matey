import xml.etree.ElementTree as ET
from pathlib import Path

__all__ = [
    "read_xml_api_key",
]


def read_xml_api_key(
    path: Path,
    element: str = "ApiKey",
) -> str:
    root = ET.parse(path).getroot()

    value = root.findtext(f".//{element}")

    if not value:
        raise ValueError(f"Could not find {element} in {path}")

    return value.strip()
