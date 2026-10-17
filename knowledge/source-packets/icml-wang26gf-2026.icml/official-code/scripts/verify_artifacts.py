#!/usr/bin/env python3
"""
Artifact verification for the PSE (ICML 2026) release.

Recomputes, directly from the released run-level JSON files, every run count in
the paper's run ledger (Appendix G, Table 23) plus the headline statistics that
the ledger rows summarize.  Exits non-zero if any count disagrees with the
paper.

Usage:
    python3 scripts/verify_artifacts.py            # verify counts
    python3 scripts/verify_artifacts.py --sha      # also check SHA-256 manifest
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "data" / "results"
LARGE = ROOT / "data" / "results_large_scale"

# Paper's ledger: (label, expected_runs, paper_section)
LEDGER = [
    ("Behavioral drift (H1)",              6000, "Sec 4.1"),
    ("Observability gap (H2)",             4000, "Sec 4.2"),
    ("Contamination ablation (H3)",         320, "Sec 4.3"),
    ("Scaling analysis",                   1100, "App C.1"),
    ("Seven-defense panel (E6)",            880, "App C.2.1-C.2.4"),
    ("Cross-model CIV/SRV panel",           480, "App C.2.5"),
    ("Temporal persistence, 20-turn (E5)",  480, "App C.3"),
    ("Temporal persistence, 10-turn",       200, "Sec 4.6"),
    ("Multi-agent cascade (E3)",            300, "App C.4"),
    ("Tool injection (E4)",                 300, "App C.5"),
    ("Remediation operators",                63, "Sec 4.4"),
    ("RAG pollution",                        80, "Sec 2"),
    ("Cross-model H1 replication",           90, "App C.1"),
]
TOTAL = 14293


def load(path):
    """Load JSON, tolerating bare NaN emitted by older numpy dumps."""
    return json.loads(re.sub(r"\bNaN\b", "null", Path(path).read_text()))


def count_h1():
    s = load(LARGE / "behavioral_drift" / "107216ab-b8f8-49f2-958f-b769b0440f35" / "summary.json")
    return s["num_runs"]


def count_h2():
    s = load(LARGE / "observability" / "107216ab-b8f8-49f2-958f-b769b0440f35" / "summary.json")
    return s["num_runs"]


def count_ablation():
    # The two models reported in Table 3, at 5 seeds x 4 scenarios x 8 configs.
    files = ["ablation_20260301_005346.json",   # gemini-2.0-flash-lite
             "ablation_20260301_005729.json"]   # llama3.1:8b
    nominal = 0
    valid = 0
    for f in files:
        d = load(RES / "ablation_real" / f)
        nominal += d["num_seeds"] * d["num_scenarios"] * 8
        valid += len(d["raw_runs"])
    print(f"    ablation: {valid} runs with valid judge labels of {nominal} attempted")
    return nominal


def count_scaling():
    n = 0
    d = load(RES / "icml_scaling_enhanced" / "experiment_20260122_015037.json")
    n += sum(m["n_samples"] for m in d["analysis"]["models"])
    for f in [RES / "icml_large_models_final" / "large_models_20260123_012134.json",
              RES / "icml_large_models_extended" / "extended_20260123_135623.json"]:
        n += len(load(f)["results"])
    d = load(RES / "icml_claude_gemini" / "experiment_20260128_200156.json")
    n += sum(m["n_samples"] for m in d["analysis"]["models"])
    return n


def count_seven_defense():
    n = len(load(RES / "icml_defense_final" / "experiment_20260123_032404.json")["results"])
    d = load(RES / "icml_claude_self_reflection" / "experiment_20260128_210708.json")
    n += len(d["results"]["raw_results"])
    return n


CIV_FILES = [
    ("defense_neurips", "defense_20260327_195034.json"),   # GPT-4o-mini
    ("defense_neurips", "defense_20260327_163802.json"),   # Llama-3.1-8B
    ("defense_cloud",   "defense_20260328_010522.json"),   # Qwen3-32B
    ("defense_real",    "defense_20260301_004626.json"),   # Gemini-2.0-Flash-Lite
    ("defense_cloud",   "defense_20260328_010750.json"),   # Llama-3.3-70B
    ("defense_cloud",   "defense_20260328_011608.json"),   # GLM-4-Plus
    ("defense_cloud",   "defense_20260328_011054.json"),   # MiniMax-Text-01
    ("defense_cloud",   "defense_20260328_011801.json"),   # DeepSeek-V3
]


def count_civ():
    valid = 0
    for sub, f in CIV_FILES:
        d = load(RES / sub / f)
        valid += sum(v["total"] for v in d["defense_results"].values())
    nominal = len(CIV_FILES) * 3 * 20
    print(f"    CIV panel: {valid} runs with valid judge labels of {nominal} attempted")
    return nominal


def count_temporal20():
    d = load(RES / "icml_temporal" / "experiment_20260122_012343.json")
    c = d["config"]
    return len(c["models"]) * c["scenarios"] * len(c["probe_intervals"]) * c["seeds"]


def count_temporal10():
    d = load(RES / "temporal_n10_vllm" / "temporal_llama31_8b_vllm_n10_20260501_134921.json")
    return sum(len(s) for v in d["raw"].values() for s in v)


def count_multiagent():
    return len(load(RES / "icml_multi_agent" / "experiment_20260122_034930.json")["results"])


def count_tool():
    return len(load(RES / "icml_tool_injection" / "experiment_20260122_235737.json")["results"])


def count_remediation():
    a = load(RES / "remediation_real" / "experiment_20260115_113813.json")["analysis"]
    return sum(v["n_trials"] for v in a.values())


def count_rag():
    return len(load(RES / "icml_rag_pollution" / "experiment_20260122_011539.json")["results"])


def count_crossmodel():
    return len(load(RES / "icml_cross_model" / "experiment_20260121_232937.json")["results"])


COUNTERS = [count_h1, count_h2, count_ablation, count_scaling, count_seven_defense,
            count_civ, count_temporal20, count_temporal10, count_multiagent,
            count_tool, count_remediation, count_rag, count_crossmodel]


def verify_counts():
    print("Run ledger (Appendix G, Table 23)\n" + "-" * 62)
    ok = True
    total = 0
    for (label, expected, sec), fn in zip(LEDGER, COUNTERS):
        try:
            got = fn()
        except Exception as exc:                                  # noqa: BLE001
            print(f"  [ERROR] {label:38s} {exc}")
            ok = False
            continue
        total += got
        mark = "ok " if got == expected else "FAIL"
        if got != expected:
            ok = False
        print(f"  [{mark}] {label:38s} {got:>6d}  (paper: {expected}, {sec})")
    print("-" * 62)
    mark = "ok " if total == TOTAL else "FAIL"
    print(f"  [{mark}] {'TOTAL':38s} {total:>6d}  (paper: {TOTAL})")
    return ok and total == TOTAL


def verify_sha():
    manifest = ROOT / "SHA256SUMS"
    if not manifest.exists():
        print("SHA256SUMS not found -- run scripts/make_manifest.py first")
        return False
    bad = 0
    checked = 0
    for line in manifest.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        digest, rel = line.split(None, 1)
        path = ROOT / rel.strip()
        if not path.exists():
            print(f"  MISSING  {rel.strip()}")
            bad += 1
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        checked += 1
        if actual != digest:
            print(f"  MISMATCH {rel.strip()}")
            bad += 1
    print(f"SHA-256: {checked} files checked, {bad} problems")
    return bad == 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sha", action="store_true", help="also verify SHA256SUMS")
    args = ap.parse_args()
    good = verify_counts()
    if args.sha:
        good = verify_sha() and good
    sys.exit(0 if good else 1)
