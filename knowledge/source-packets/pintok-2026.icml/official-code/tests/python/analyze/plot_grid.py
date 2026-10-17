#!/usr/bin/env python3
"""
Create 3x4 grid plot.

# Grid layout
"""

import argparse
import os
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator, FuncFormatter, LogLocator, LogFormatterMathtext

# Imports
import sys
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if THIS_DIR not in sys.path:
    sys.path.append(THIS_DIR)
import plot_results


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Create 3x4 grid")
    p.add_argument("--csv", required=True, help="Path to results_summary.csv")
    p.add_argument("--out-dir", required=True, help="Directory to save the grid plot")
    p.add_argument("--title", default=None, help="Optional figure-wide title")
    p.add_argument("--outfile", default="plot_grid_3x4.pdf", help="Output filename (PDF)")
    p.add_argument("--log-y", action="store_true", help="Use logarithmic scale for Y axis")
    return p.parse_args()


DATASET_ROWS = ["openwebtext", "code", "multilingual"]
DATASET_TITLES = {
    "openwebtext": "OpenWebText",
    "code": "Code",
    "multilingual": "Multilingual",
}
METRIC_COLS = ["avg", "p50", "p90", "p99"]
METRIC_TITLES = {"avg": "Average", "p50": "P50", "p90": "P90", "p99": "P99"}

COLORS = {"python": "#FDB515", "rust": "#002676", "pintok": "#8C1515"}
LABELS = {"python": "Python", "rust": "Rust", "pintok": "PinTok"}


def plot_cell(ax, series: Dict[str, List[Tuple[int, float, float]]], log_y: bool = False):
    any_points = False
    for mode in ["python", "rust", "pintok"]:
        pts = series.get(mode, [])
        if not pts:
            continue
        any_points = True
        xs = [t for (t, _, _) in pts]
        ys = [m for (_, m, _) in pts]
        es = [s for (_, _, s) in pts]
        if len(xs) == 1:
            ax.scatter(xs, ys, color=COLORS[mode], label=LABELS[mode], marker='o', s=12, linewidths=0.0)
        else:
            ax.plot(xs, ys, color=COLORS[mode], label=LABELS[mode], marker='o', linewidth=1.2, markersize=2.5)
            # No confidence band for log plots
            if (not log_y) and any(e > 0 for e in es):
                lower = [y - e for y, e in zip(ys, es)]
                upper = [y + e for y, e in zip(ys, es)]
                ax.fill_between(xs, lower, upper, color=COLORS[mode], alpha=0.15, linewidth=0)

    ax.grid(True, linestyle='--', alpha=0.25, linewidth=0.4)
    ax.set_xlim(0, 2100)
    ax.set_xticks([500, 1000, 1500, 2000])
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, p: f"{int(x):,}"))
    # Y-axis format
    if log_y:
        ax.set_yscale('log')
        ax.yaxis.set_major_locator(LogLocator(base=10.0))
        ax.yaxis.set_major_formatter(LogFormatterMathtext())
    else:
        ax.yaxis.set_major_locator(MaxNLocator(nbins=4, prune='both'))


def main():
    args = parse_args()

    rows = plot_results.load_results(args.csv)
    if not rows:
        print(f"No rows found in {args.csv}")
        return

    os.makedirs(args.out_dir, exist_ok=True)

    plt.rcParams.update({
        'font.size': 6.5,
        'axes.titlesize': 6.5,
        'axes.labelsize': 6.0,
        'xtick.labelsize': 4.0,
        'ytick.labelsize': 5.0,
        'legend.fontsize': 5.5,
        'axes.linewidth': 0.6,
        'xtick.major.width': 0.5,
        'ytick.major.width': 0.5,
        'xtick.major.size': 2.0,
        'ytick.major.size': 2.0,
        'grid.linewidth': 0.4,
    })

    fig, axs = plt.subplots(3, 4, figsize=(4.6, 2.72))

    # Compute row limits
    import math
    row_y_limits = {}
    for r, dataset in enumerate(DATASET_ROWS):
        y_min = math.inf
        y_max = -math.inf
        for metric in METRIC_COLS:
            series = plot_results.build_series(rows, dataset, metric)
            for mode in ["python", "rust", "pintok"]:
                pts = series.get(mode, [])
                for _, mean, std in pts:
                    if args.log_y:
                        y_min = min(y_min, mean)
                        y_max = max(y_max, mean)
                    else:
                        y_min = min(y_min, mean - std)
                        y_max = max(y_max, mean + std)
        if y_min == math.inf or y_max == -math.inf:
            y_min, y_max = 1.0, 100000.0
        if args.log_y:
            y_min = max(y_min, 1e-12)
            factor = 1.2
            row_y_limits[r] = (y_min / factor, y_max * factor)
        else:
            y_min = max(0.0, y_min)
            span = max(1e-9, y_max - y_min)
            pad = 0.05 * span
            row_y_limits[r] = (max(0.0, y_min - pad), y_max + pad)

    # Plot cells
    for r, dataset in enumerate(DATASET_ROWS):
        for c, metric in enumerate(METRIC_COLS):
            ax = axs[r, c]
            series = plot_results.build_series(rows, dataset, metric)
            plot_cell(ax, series, log_y=args.log_y)

            if r in row_y_limits:
                y_min, y_max = row_y_limits[r]
                ax.set_ylim(y_min, y_max)

            if r == 0:
                ax.set_title(METRIC_TITLES[metric])

            if c == 0:
                ax.set_ylabel(f"{DATASET_TITLES.get(dataset, dataset)}\nLatency (us)")
                ax.tick_params(axis='y', which='both', labelleft=True)
            else:
                ax.tick_params(axis='y', which='both', labelleft=False)

            if r == 2:
                ax.set_xlabel("Tokens")
            else:
                ax.set_xticklabels([])

    # Legend
    # Collect handles
    handles = []
    labels = []
    for r in range(3):
        for c in range(4):
            h, l = axs[r, c].get_legend_handles_labels()
            if h and l:
                handles, labels = h, l
                break
        if handles and labels:
            break

    ordered_handles = []
    ordered_labels = []
    for desired_label in ["Python", "Rust", "PinTok"]:
        if desired_label in labels:
            idx = labels.index(desired_label)
            ordered_handles.append(handles[idx])
            ordered_labels.append(labels[idx])

    fig.tight_layout(rect=[0.01, 0.01, 0.97, 0.99])
    if ordered_handles and ordered_labels:
        fig.legend(
            ordered_handles,
            ordered_labels,
            loc='center left',
            ncol=1,
            frameon=False,
            bbox_to_anchor=(0.975, 0.5),
            borderaxespad=0.0,
            handlelength=1.5,
            handletextpad=0.5,
            markerscale=1.0,
            borderpad=0.2,
        )

    if args.title:
        fig.suptitle(args.title, y=0.99)

    out_path = os.path.join(args.out_dir, args.outfile)
    fig.savefig(out_path, bbox_inches='tight', pad_inches=0.02)
    print(f"Saved grid plot to {out_path}")
    plt.close(fig)


if __name__ == "__main__":
    main()
