from pathlib import Path
from typing import Any, Dict, List
import os
import yaml

from dotenv import load_dotenv


def load_yaml(path: str | Path) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config not found: {p}")
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_dotenv_required(dotenv_path: str = ".env") -> None:
    p = Path(dotenv_path)
    if not p.exists():
        raise FileNotFoundError(f".env not found at: {p.resolve()}")
    load_dotenv(dotenv_path=str(p))


def require_env(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise RuntimeError(f"Missing required env var: {name}")
    return v


def require_env_many(keys: List[str]) -> None:
    missing = [k for k in keys if not os.getenv(k)]
    if missing:
        raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")
