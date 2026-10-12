"""Load the preserved upstream agents alongside benchmark-specific adapters."""
from pathlib import Path

_UPSTREAM_AGENTS = (Path(__file__).resolve().parents[3] / "code" /
                    "reference_examples" / "terminal_bench_2" / "agents")
if not (_UPSTREAM_AGENTS / "baseline_kira.py").is_file():
    raise ImportError(f"Missing official KIRA snapshot: {_UPSTREAM_AGENTS}")
__path__.append(str(_UPSTREAM_AGENTS))
