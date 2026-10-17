"""Case4 metrics persistence and comparison table output."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, Optional


def _fmt(v: Optional[float]) -> str:
    if v is None:
        return ""
    return f"{v:.6f}"


def _improvement_lower_better(base: Optional[float], tool: Optional[float]) -> str:
    if base in (None, 0) or tool is None:
        return ""
    return f"{((base - tool) / base) * 100.0:.2f}%"


def _improvement_higher_better(base: Optional[float], tool: Optional[float]) -> str:
    if base is None or tool is None:
        return ""
    return f"{(tool - base) * 100.0:.2f}pp"


def update_metrics_store(results_dir: Path, mode: str, metrics: Dict[str, Optional[float]]) -> Dict:
    results_dir.mkdir(parents=True, exist_ok=True)
    store_path = results_dir / "case4_metrics_store.json"
    if store_path.is_file():
        store = json.loads(store_path.read_text(encoding="utf-8"))
    else:
        store = {"baseline": {}, "toolpro": {}}
    store[mode] = metrics
    store_path.write_text(json.dumps(store, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return store


def write_compare_csv(results_dir: Path, store: Dict) -> Path:
    results_dir.mkdir(parents=True, exist_ok=True)
    out = results_dir / "case4_metrics_comparison.csv"
    b = store.get("baseline") or {}
    t = store.get("toolpro") or {}
    rows = [
        (
            "Average Latency (s)",
            _fmt(b.get("average_latency_s")),
            _fmt(t.get("average_latency_s")),
            _improvement_lower_better(b.get("average_latency_s"), t.get("average_latency_s")),
        ),
        (
            "Client-side Traffic (bytes)",
            _fmt(b.get("client_traffic_bytes")),
            _fmt(t.get("client_traffic_bytes")),
            _improvement_lower_better(b.get("client_traffic_bytes"), t.get("client_traffic_bytes")),
        ),
        (
            "Success Rate (accuracy)",
            _fmt(b.get("success_rate")),
            _fmt(t.get("success_rate")),
            _improvement_higher_better(b.get("success_rate"), t.get("success_rate")),
        ),
        (
            "Fallback Rate",
            _fmt(b.get("fallback_rate")),
            _fmt(t.get("fallback_rate")),
            "",
        ),
    ]
    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Metric", "Baseline (stepwise)", "ToolPro (program mode)", "Improvement"])
        writer.writerows(rows)
    return out
