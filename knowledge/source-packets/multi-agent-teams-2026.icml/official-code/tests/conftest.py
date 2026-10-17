"""Test configuration helpers."""

import sys
from pathlib import Path


def _ensure_project_on_path() -> None:
    """Add the project root to sys.path so tests can import the package."""

    project_root = Path(__file__).resolve().parents[1]
    project_str = str(project_root)
    if project_str not in sys.path:
        sys.path.insert(0, project_str)


_ensure_project_on_path()
