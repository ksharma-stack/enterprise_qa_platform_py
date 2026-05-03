"""Utility: normalize artifact paths"""

from __future__ import annotations
from pathlib import Path


def mkdir(path: str) -> str:
    """Create a directory at the given path, including parent directories if needed.

    Args:
        path: The directory path to create.

    Returns:
        The path that was created.
    """
    Path(path).mkdir(parents=True, exist_ok=True)
    return path

