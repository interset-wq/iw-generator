"""Utility functions for file and path operations."""

from __future__ import annotations

import shutil
from pathlib import Path


def copy_tree(src: Path, dst: Path) -> None:
    """Copy a directory tree, merging into existing destination."""
    if not src.is_dir():
        return
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        s = src / item.name
        d = dst / item.name
        if s.is_dir():
            copy_tree(s, d)
        else:
            shutil.copy2(s, d)


def ensure_dir(path: Path) -> None:
    """Ensure a directory exists."""
    path.mkdir(parents=True, exist_ok=True)


def clean_dir(path: Path) -> None:
    """Remove and recreate a directory."""
    if path.exists():
        for _ in range(3):
            try:
                shutil.rmtree(path)
                break
            except PermissionError:
                import time

                time.sleep(0.1)
    path.mkdir(parents=True, exist_ok=True)
