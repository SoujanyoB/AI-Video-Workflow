"""
utils.py

General helper utilities.
"""

from __future__ import annotations

from pathlib import Path


def ensure_directory(path: Path) -> Path:
    """
    Create a directory if it doesn't exist.
    """

    path.mkdir(parents=True, exist_ok=True)

    return path