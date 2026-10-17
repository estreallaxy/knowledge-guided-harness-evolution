#!/usr/bin/env python3
"""
Plot latency vs tokens.

Usage examples:
  # Plot average latency
  python tests/python/analyze/plot_results.py \
    --csv tests/python/analyze/results_summary.csv \
    --dataset openwebtext --metric avg \
    --out-dir tests/python/analyze/plots

  # Plot P50
  python tests/python/analyze/plot_results.py --metric p50 --all-datasets

  # Plot P99
  python tests/python/analyze/plot_results.py --dataset multilingual code --metric p99
"""

import argparse
import csv
import os
from collections import defaultdict
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, LogLocator, LogFormatterMathtext


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Plot latency vs tokens from results_summary.csv")
    p.add_argument("--csv", default="tests/python/analyze/results_summary.csv",
                   help="Path to results CSV produced by run_experiments.py")
    grp = p.add_mutually_exclusive_group()
    grp.add_argument("--dataset", nargs="*", default=None,
                     help="Dataset(s) to plot (e.g., openwebtext multilingual code)")
    grp.add_argument("--all-datasets", action="store_true",
                     help="Plot all datasets present in the CSV")
    p.add_argument("--metric", choices=["avg", "p50", "p90", "p99"], default="avg",
                   help="Which latency group to plot (default: avg)")
    p.add_argument("--title", default=None, help="Optional figure title")
    p.add_argument("--out-dir", default="tests/python/analyze/plots",
                   help="Directory to write PDF plots")
    p.add_argument("--show", action="store_true", help="Show plot windows interactively")
    p.add_argument("--log-y", action="store_true", help="Use logarithmic scale for Y axis and add _logy suffix")
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


def build_series(rows: List[Dict[str, str]], dataset: str, metric: str) -> Dict[str, List[Tuple[int, float, float]]]:
    """Build series sorted by tokens."""
    # Metric columns
    col = {
        "pintok": (f"{metric}_pintok_mean_us", f"{metric}_pintok_std_us"),
        "rust": (f"{metric}_rust_mean_us", f"{metric}_rust_std_us"),
        "python": (f"{metric}_python_mean_us", f"{metric}_python_std_us"),
        "embed": (f"{metric}_embed_mean_us", f"{metric}_embed_std_us"),
    }
    series = {"pintok": [], "rust": [], "python": [], "embed": []}
    for r in rows:
        if r.get("dataset") != dataset:
            continue
        tokens = r.get("tokens_per_packet")
        try:
            tokens = int(float(tokens)) if tokens is not None else None
        except Exception:
            continue
        for mode, (mcol, scol) in col.items():
            mean = to_float(r.get(mcol))
            std = to_float(r.get(scol))
            if mean is not None:
                series[mode].append((tokens, mean, std or 0.0))
    for mode in list(series.keys()):
        series[mode].sort(key=lambda t: t[0])
    return series


def plot_dataset(dataset: str, rows: List[Dict[str, str]], metric: str, out_dir: str, title: str = None, show: bool = False, log_y: bool = False):
    data = build_series(rows, dataset, metric)

    ensure_out_dir(out_dir)
    fig, ax = plt.subplots(figsize=(8, 5))

    # Colors
    colors = {"pintok": "#8C1515", "rust": "#002676", "python": "#FDB515", "embed": "#555555"}
    labels = {"pintok": "PinTok", "rust": "Rust", "python": "Python", "embed": "ModelOnly"}

    any_points = False
    for mode in ["pintok", "rust", "python", "embed"]:
        pts = data.get(mode, [])
        if not pts:
            continue
        any_points = True
        xs = [t for (t, _, _) in pts]
        ys = [m for (_, m, _) in pts]
        es = [s for (_, _, s) in pts]
        if len(xs) == 1:
            ax.scatter(xs, ys, color=colors[mode], label=labels[mode], marker='o', s=60)
        else:
            ax.plot(xs, ys, color=colors[mode], label=labels[mode], marker='o', linewidth=2)
            if any(e > 0 for e in es):
                lower = [y - e if (y is not None and e is not None) else None for y, e in zip(ys, es)]
                upper = [y + e if (y is not None and e is not None) else None for y, e in zip(ys, es)]
                # Filter out None entries just in case
                band_x, band_lo, band_hi = [], [], []
                for x, lo, hi in zip(xs, lower, upper):
                    if lo is None or hi is None:
                        continue
                    band_x.append(x)
                    band_lo.append(lo)
                    band_hi.append(hi)
                if len(band_x) >= 2:
                    ax.fill_between(band_x, band_lo, band_hi, color=colors[mode], alpha=0.15, linewidth=0)

    # Format axes
    ax.set_xlabel("Sequence length (tokens)")
    ax.set_ylabel("Latency (us)")
    # X-axis settings
    ax.set_xlim(0, 2100)
    ax.set_xticks([500, 1000, 1500, 2000])
    # Format x-ticks
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, p: f"{int(x):,}"))
    # Font sizes
    ax.tick_params(axis='y', labelsize=9)
    ax.tick_params(axis='x', labelsize=8)
    if log_y:
        ax.set_yscale('log')
        ax.yaxis.set_major_locator(LogLocator(base=10.0))
        ax.yaxis.set_major_formatter(LogFormatterMathtext())
    title_suffix = {"avg": "Average", "p50": "P50", "p90": "P90", "p99": "P99"}[metric]
    # Extract metadata
    ds_rows = [r for r in rows if r.get('dataset') == dataset]
    trials_vals = sorted({r.get('trials') for r in ds_rows if r.get('trials')})
    packets_vals = sorted({r.get('packets') for r in ds_rows if r.get('packets')})
    trials_str = trials_vals[-1] if trials_vals else ''
    packets_str = packets_vals[-1] if packets_vals else ''
    meta_parts = []
    if trials_str:
        meta_parts.append(f"{trials_str} trials")
    if packets_str:
        meta_parts.append(f"{packets_str} packets")
    meta = f" ({', '.join(meta_parts)})" if meta_parts else ""
    ax.set_title(title or f"{dataset} – {title_suffix} latency{meta}")
    ax.grid(True, linestyle='--', alpha=0.3)
    if any_points:
        ax.legend()

    suffix = "_logy" if log_y else ""
    out_path = os.path.join(out_dir, f"plot_{dataset}_{metric}{suffix}.pdf")
    fig.tight_layout()
    # Save as vector PDF (no DPI needed)
    fig.savefig(out_path)
    print(f"Saved plot to {out_path}")
    if show:
        plt.show()
    plt.close(fig)


def main():
    args = parse_args()
    rows = load_results(args.csv)
    if not rows:
        print(f"No rows found in {args.csv}")
        return

    # Determine datasets to plot
    if args.all_datasets or not args.dataset:
        datasets = sorted({r.get('dataset', '') for r in rows if r.get('dataset')})
    else:
        datasets = args.dataset

    for ds in datasets:
        plot_dataset(ds, rows, args.metric, args.out_dir, title=args.title, show=args.show, log_y=args.log_y)


if __name__ == "__main__":
    main()
