from dataclasses import dataclass
from pathlib import Path
import re


def find_repo_root(start: Path | None = None) -> Path:
    p = (start or Path.cwd()).resolve()
    for cur in [p, *p.parents]:
        if (cur / "pyproject.toml").exists() or (cur / ".git").exists():
            return cur
    return p
