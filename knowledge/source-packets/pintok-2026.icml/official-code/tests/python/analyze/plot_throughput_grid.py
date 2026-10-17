#!/usr/bin/env python3
"""
Throughput 1x3 grid comparison.

# Compare throughput across datasets
"""

import argparse
import os
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

import csv


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Create a 1x3 throughput grid from throughput_summary.csv or results_summary.csv")
    p.add_argument("--csv", required=True, help="Path to throughput_summary.csv or results_summary.csv")
    p.add_argument("--out-dir", required=True, help="Directory to save the grid plot")
    p.add_argument("--outfile", default="plot_throughput_grid_1x3.pdf", help="Output filename (PDF)")
    return p.parse_args()


DATASETS = ["openwebtext", "code", "multilingual"]
DATASET_TITLES = {"openwebtext": "OpenWebText", "code": "Code", "multilingual": "Multilingual"}
COLORS = {"python": "#FDB515", "rust": "#002676", "pintok": "#8C1515"}
LABELS = {"python": "Python", "rust": "Rust", "pintok": "PinTok"}


def load_rows(csv_path: str) -> List[Dict[str, str]]:
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows


def to_float(s):
    try:
        return float(s)
    except Exception:
        return None


def build_series(rows: List[Dict[str, str]], dataset: str) -> Dict[str, List[Tuple[int, float, float]]]:
    """Build throughput series for dataset."""
    # Detect schema
    has_tps = any('pintok_tps_mean' in r for r in rows) or any(
        'pintok_tps_mean' in k for r in rows for k in r.keys()
    )

    series = {"pintok": [], "rust": [], "python": []}
    if has_tps:
        col = {
            "pintok": ("pintok_tps_mean", "pintok_tps_std"),
            "rust": ("rust_tps_mean", "rust_tps_std"),
            "python": ("python_tps_mean", "python_tps_std"),
        }
        for r in rows:
            if r.get('dataset') != dataset:
                continue
            try:
                tokens = int(float(r.get('tokens_per_packet', '')))
            except Exception:
                continue
            for mode, (mcol, scol) in col.items():
                mean = to_float(r.get(mcol))
                std = to_float(r.get(scol))
                if mean is not None:
                    series[mode].append((tokens, mean, std or 0.0))
    else:
        # Convert results_summary rows to throughput
        # Expect columns: avg_pintok_mean_us, avg_pintok_std_us, etc.
        def tf(mu_us: str | None, sd_us: str | None, tokens: int) -> Tuple[float | None, float | None]:
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
            if r.get('dataset') != dataset:
                continue
            try:
                tokens = int(float(r.get('tokens_per_packet', '')))
            except Exception:
                continue
            dpdk_m, dpdk_s = tf(r.get('avg_pintok_mean_us'), r.get('avg_pintok_std_us'), tokens)
            rust_m, rust_s = tf(r.get('avg_rust_mean_us'), r.get('avg_rust_std_us'), tokens)
            py_m, py_s = tf(r.get('avg_python_mean_us'), r.get('avg_python_std_us'), tokens)
            if dpdk_m is not None:
                series['pintok'].append((tokens, dpdk_m, dpdk_s or 0.0))
            if rust_m is not None:
                series['rust'].append((tokens, rust_m, rust_s or 0.0))
            if py_m is not None:
                series['python'].append((tokens, py_m, py_s or 0.0))

    for mode in list(series.keys()):
        series[mode].sort(key=lambda t: t[0])
    return series


def plot_cell(ax, series: Dict[str, List[Tuple[int, float, float]]], y_limits=None):
    """Grouped bar plot."""
    # Group positions
    all_tokens = sorted({t for mode in series.values() for (t, _, _) in mode})
    n_groups = len(all_tokens)
    # Alignment index
    token_index = {t: i for i, t in enumerate(all_tokens)}
    x_centers = list(range(n_groups))
    ax.set_xticks(x_centers)
    ax.set_xticklabels([f"{t:,}" for t in all_tokens])

    # Bar layout: Python left, Rust middle, PinTok right
    bar_width = 0.26 if n_groups > 1 else 0.28
    offsets = {
        'python': -bar_width,
        'rust': 0.0,
        'pintok': bar_width,
    }

    for mode in ["python", "rust", "pintok"]:
        pts = series.get(mode, [])
        if not pts:
            continue
        xs = [token_index[t] + offsets[mode] for (t, _, _) in pts]
        ys = [m for (_, m, _) in pts]
        es = [s for (_, _, s) in pts]
        # Draw bars with thin error bars + caps
        ax.bar(
            xs,
            ys,
            width=bar_width,
            color=COLORS[mode],
            label=LABELS[mode],
            linewidth=0.0,
            yerr=es if any(e > 0 for e in es) else None,
            error_kw=dict(ecolor='black', elinewidth=0.7, capsize=2.0, capthick=0.7),
        )

    # Styling
    ax.grid(True, linestyle='--', alpha=0.25, linewidth=0.4, axis='y')
    ax.set_xlim(-0.6, max(x_centers) + 0.6 if x_centers else 0.4)
    # Shared limits
    if y_limits:
        ax.set_ylim(y_limits)


def main():
    args = parse_args()
    rows = load_rows(args.csv)
    if not rows:
        print(f"No rows found in {args.csv}")
        return

    os.makedirs(args.out_dir, exist_ok=True)

    plt.rcParams.update({
        'font.size': 7.0,
        'axes.titlesize': 7.0,
        'axes.labelsize': 6.8,
        'xtick.labelsize': 4.5,
        'ytick.labelsize': 6.2,
        'legend.fontsize': 6.4,
        'axes.linewidth': 0.6,
        'xtick.major.width': 0.5,
        'ytick.major.width': 0.5,
        'xtick.major.size': 2.0,
        'ytick.major.size': 2.0,
        'grid.linewidth': 0.4,
    })

    fig, axs = plt.subplots(1, 3, figsize=(5.2, 1.44))

    # Compute shared limits
    import math
    y_min = math.inf
    y_max = -math.inf
    all_series = {}
    for dataset in DATASETS:
        series = build_series(rows, dataset)
        all_series[dataset] = series
        for mode in ["python", "rust", "pintok"]:
            for _, mean, std in series.get(mode, []):
                y_min = min(y_min, mean - std if std else mean)
                y_max = max(y_max, mean + std if std else mean)

    if y_min == math.inf or y_max == -math.inf:
        y_min, y_max = 0, 100000
    else:
        y_min = max(0, y_min)
        span = y_max - y_min
        pad = 0.05 * span
        y_min = max(0, y_min - pad)
        y_max = y_max + pad

    shared_y_limits = (y_min, y_max)

    for c, dataset in enumerate(DATASETS):
        ax = axs[c]
        series = all_series[dataset]
        plot_cell(ax, series, y_limits=shared_y_limits)
        ax.set_title(DATASET_TITLES.get(dataset, dataset))
        if c == 0:
            ax.set_ylabel("Throughput\n(tokens/s)")
        else:
            ax.set_yticklabels([])
        ax.set_xlabel("Tokens")

    # Legend
    handles, labels = axs[0].get_legend_handles_labels()
    desired = ["Python", "Rust", "PinTok"]
    if handles and labels:
        map_h = {l: h for h, l in zip(handles, labels)}
        labels = [l for l in desired if l in map_h]
        handles = [map_h[l] for l in labels]
    fig.tight_layout(rect=[0.01, 0.01, 0.88, 0.99])
    if handles and labels:
        fig.legend(handles, labels, loc='center left', ncol=1, frameon=False, bbox_to_anchor=(0.90, 0.5), borderaxespad=0.0, handlelength=1.5, handletextpad=0.5, markerscale=1.0, borderpad=0.2)

    out_path = os.path.join(args.out_dir, args.outfile)
    fig.savefig(out_path, bbox_inches='tight', pad_inches=0.02)
    print(f"Saved throughput grid to {out_path}")


if __name__ == "__main__":
    main()
