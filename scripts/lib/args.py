"""Shared command-line argument parsing.

Import parse_args in a script and run it before anything else, i.e.
immediately after if __name__ == "__main__".
"""

import argparse
from pathlib import Path

__all__ = [
    "parse_args",
]


def parse_args() -> argparse.Namespace:
    """Parse shared command-line arguments."""

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-e",
        "--env-file",
        type=Path,
        required=True,
        help="Path to the environment/configuration file.",
    )

    return parser.parse_args()
