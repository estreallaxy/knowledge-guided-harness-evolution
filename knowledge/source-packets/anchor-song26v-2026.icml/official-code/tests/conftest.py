"""Shared pytest configuration for offline ANCHOR tests."""

from pathlib import Path

import pytest


@pytest.fixture
def repo_root() -> Path:
    """Return the repository root independent of the test working directory."""
    return Path(__file__).resolve().parents[1]

