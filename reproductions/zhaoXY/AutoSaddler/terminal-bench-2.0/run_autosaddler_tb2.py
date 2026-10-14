#!/usr/bin/env python
"""Run the *unmodified* AutoSaddler V2 engine against the TB2 scenario plugin.

Why a driver instead of the upstream CLI: the engine has no OpenAI-compatible provider
type, and `Registry` exposes no public provider-registration API. This script builds the
standard registry, adds a `litellm` provider (the unit's deepseek transport), and hands
that registry to the official `build_runtime` entry point -- so the vendored `code/`
tree stays byte-identical to upstream.

Usage:
    ../../code/.venv/bin/python run_autosaddler_tb2.py \
        --config configs/tb2_terminus_deepseek.yaml --run-id tb2-smoke [--max-iterations 1]

Run with a *neutral* cwd if you also launch harbor by hand; the engine itself is
cwd-independent. DEEPSEEK_API_KEY is read from `runner/.env` (never from the repo).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

UNIT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(UNIT_DIR / "plugin"))

from autosaddler.v2.config.registry import build_runtime, default_registry  # noqa: E402

from litellm_provider import build_litellm_provider  # noqa: E402

DEFAULT_CONFIG = UNIT_DIR / "configs" / "tb2_terminus_deepseek.yaml"
ENV_FILE = UNIT_DIR / "runner" / ".env"


def load_env_file(path: Path) -> list[str]:
    loaded: list[str] = []
    if not path.exists():
        return loaded
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key and key not in os.environ:
            os.environ[key] = value.strip().strip('"').strip("'")
            loaded.append(key)
    return loaded


def build_registry():
    registry = default_registry()
    registry.providers["litellm"] = build_litellm_provider
    return registry


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--max-iterations", type=int, default=None,
                        help="override optimization.budget.max_iterations (dry planning aid)")
    parser.add_argument("--check-only", action="store_true",
                        help="build the runtime and exit without evaluating anything")
    args = parser.parse_args()

    loaded = load_env_file(ENV_FILE)
    if "DEEPSEEK_API_KEY" not in os.environ:
        print("ERROR: DEEPSEEK_API_KEY is not set (expected in runner/.env)", file=sys.stderr)
        return 127

    config_path = args.config.resolve()
    if args.max_iterations is not None:
        # Overriding the budget keeps the config file as the single source of truth for
        # everything else; only max_iterations may differ per invocation (matches fork rules).
        text = config_path.read_text(encoding="utf-8")
        config_path = config_path.with_name(f"{config_path.stem}.{args.run_id}.yaml")
        lines = []
        for line in text.splitlines():
            if line.strip().startswith("max_iterations:"):
                indent = line[: len(line) - len(line.lstrip())]
                lines.append(f"{indent}max_iterations: {args.max_iterations}")
            else:
                lines.append(line)
        config_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    started = time.time()
    registry = build_registry()
    runtime = build_runtime(config_path, run_id=args.run_id, registry=registry)
    print(json.dumps({"run_id": args.run_id, "config": str(config_path),
                      "env_keys_loaded": loaded,
                      "scenario": runtime.scenario.name if hasattr(runtime, "scenario") else None},
                     indent=2, ensure_ascii=False))
    if args.check_only:
        print("check-only: runtime assembled; no evaluation was started.")
        return 0

    result = runtime.engine.run()
    elapsed = time.time() - started
    summary = {
        "run_id": args.run_id,
        "elapsed_s": round(elapsed, 1),
        "selected_candidate_id": getattr(result, "selected_candidate_id", None),
        "development_score": getattr(result, "development_score", None),
        "result_type": type(result).__name__,
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    out_path = UNIT_DIR / "runs" / f"{args.run_id}-driver-summary.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
