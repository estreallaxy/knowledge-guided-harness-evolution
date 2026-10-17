#!/usr/bin/env python3
"""
Plot throughput vs tokens.

Usage examples:
  python tests/python/analyze/plot_throughput_results.py \
    --csv tests/python/analyze/results/<test>/throughput_summary.csv \
    --all-datasets

  python tests/python/analyze/plot_throughput_results.py \
    --csv tests/python/analyze/results/<test>/throughput_summary.csv \
    --dataset openwebtext code
"""

import argparse
import csv
import os
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Plot throughput")
    p.add_argument("--csv", required=True, help="Path to throughput_summary.csv or results_summary.csv")
    grp = p.add_mutually_exclusive_group()
    grp.add_argument("--dataset", nargs="*", default=None,
                     help="Dataset(s) to plot (e.g., openwebtext multilingual code)")
    grp.add_argument("--all-datasets", action="store_true",
                     help="Plot all datasets present in the CSV")
    p.add_argument("--title", default=None, help="Optional figure title")
    p.add_argument("--out-dir", default="tests/python/analyze/plots",
                   help="Directory to write PDF plots")
    return p.parse_args()


def load_results(csv_path: str) -> List[Dict[str, str]]:
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        return list(reader)


def to_float(s):
    try:
        return float(s)
    except Exception:
        return None


def ensure_out_dir(path: str):
    os.makedirs(path, exist_ok=True)


def build_series(rows: List[Dict[str, str]], dataset: str) -> Dict[str, List[Tuple[int, float, float]]]:
    # Use TPS columns or compute from latency
    has_tps = any('pintok_tps_mean' in r for r in rows) or any(
        'pintok_tps_mean' in k for r in rows for k in r.keys()
    )
    series = {"pintok": [], "rust": [], "python": [], "embed": []}
    if has_tps:
        col = {
            "pintok": ("pintok_tps_mean", "pintok_tps_std"),
            "rust": ("rust_tps_mean", "rust_tps_std"),
            "python": ("python_tps_mean", "python_tps_std"),
            "embed": ("embed_tps_mean", "embed_tps_std"),
        }
        for r in rows:
            if r.get("dataset") != dataset:
                continue
            try:
                tokens = int(float(r.get("tokens_per_packet", "")))
            except Exception:
                continue
            for mode, (mcol, scol) in col.items():
                mean = to_float(r.get(mcol))
                std = to_float(r.get(scol))
                if mean is not None:
                    series[mode].append((tokens, mean, std or 0.0))
    else:
        def tf(mu_us: str | None, sd_us: str | None, tokens: int):
            try:
                mu = float(mu_us) if mu_us else None
                sd = float(sd_us) if sd_us else None
            except Exception:
                return (None, None)
            if mu and mu > 0:
                mean_tps = tokens * 1_000_000.0 / mu
                std_tps = (tokens * 1_000_000.0 * sd / (mu * mu)) if (sd is not None) else 0.0
                return (mean_tps, std_tps)
            return (None, None)
        for r in rows:
            if r.get("dataset") != dataset:
                continue
            try:
                tokens = int(float(r.get("tokens_per_packet", "")))
            except Exception:
                continue
            dpdk_m, dpdk_s = tf(r.get('avg_pintok_mean_us'), r.get('avg_pintok_std_us'), tokens)
            rust_m, rust_s = tf(r.get('avg_rust_mean_us'), r.get('avg_rust_std_us'), tokens)
            py_m, py_s = tf(r.get('avg_python_mean_us'), r.get('avg_python_std_us'), tokens)
            em_m, em_s = tf(r.get('avg_embed_mean_us'), r.get('avg_embed_std_us'), tokens)
            if dpdk_m is not None:
                series['pintok'].append((tokens, dpdk_m, dpdk_s or 0.0))
            if rust_m is not None:
                series['rust'].append((tokens, rust_m, rust_s or 0.0))
            if py_m is not None:
                series['python'].append((tokens, py_m, py_s or 0.0))
            if em_m is not None:
                series['embed'].append((tokens, em_m, em_s or 0.0))
    for mode in list(series.keys()):
        series[mode].sort(key=lambda t: t[0])
    return series


def plot_dataset(dataset: str, rows: List[Dict[str, str]], out_dir: str, title: str = None):
    data = build_series(rows, dataset)

    ensure_out_dir(out_dir)
    # Dimensions
    fig, ax = plt.subplots(figsize=(5.6, 3.0))

    colors = {"pintok": "#8C1515", "rust": "#002676", "python": "#FDB515", "embed": "#555555"}
    labels = {"pintok": "PinTok", "rust": "Rust", "python": "Python", "embed": "ModelOnly"}

    # Bar grouping
    all_tokens = sorted({t for mode in data.values() for (t, _, _) in mode})
    token_index = {t: i for i, t in enumerate(all_tokens)}
    centers = list(range(len(all_tokens)))
    ax.set_xticks(centers)
    ax.set_xticklabels([f"{t:,}" for t in all_tokens])
    width = 0.28 if len(centers) <= 1 else 0.26
    # Bar offsets
    offsets = {'python': -width, 'rust': 0.0, 'pintok': width}

    any_points = False
    for mode in ["python", "rust", "pintok", "embed"]:
        pts = data.get(mode, [])
        if not pts:
            continue
        any_points = True
        xs = [token_index[t] + offsets[mode] for (t, _, _) in pts]
        ys = [m for (_, m, _) in pts]
        es = [s for (_, _, s) in pts]
        ax.bar(
            xs,
            ys,
            width=width,
            color=colors[mode],
            label=labels[mode],
            linewidth=0.0,
            yerr=es if any(e > 0 for e in es) else None,
            error_kw=dict(ecolor='black', elinewidth=0.8, capsize=2.0, capthick=0.8),
        )

    ax.set_xlabel("Tokens")
    ax.set_ylabel("Throughput (tokens/s)")
    ax.grid(True, linestyle='--', alpha=0.3, axis='y')
    if any_points:
        # Legend order
        h, l = ax.get_legend_handles_labels()
        desired = ["PinTok", "Rust", "Python"]
        m = {label: handle for handle, label in zip(h, l)}
        labels = [x for x in desired if x in m]
        handles = [m[x] for x in labels]
        ax.legend(handles, labels, loc='best')

    out_path = os.path.join(out_dir, f"throughput_{dataset}.pdf")
    fig.subplots_adjust(left=0.10, right=0.995, top=0.92, bottom=0.16)
    fig.savefig(out_path, bbox_inches='tight', pad_inches=0.02)
    print(f"Saved plot to {out_path}")
    plt.close(fig)


def main():
    args = parse_args()
    rows = load_results(args.csv)
    if not rows:
        print(f"No rows found in {args.csv}")
        return

    if args.all_datasets or not args.dataset:
        datasets = sorted({r.get('dataset', '') for r in rows if r.get('dataset')})
    else:
        datasets = args.dataset

    for ds in datasets:
        plot_dataset(ds, rows, args.out_dir, title=args.title)


if __name__ == "__main__":
    main()
