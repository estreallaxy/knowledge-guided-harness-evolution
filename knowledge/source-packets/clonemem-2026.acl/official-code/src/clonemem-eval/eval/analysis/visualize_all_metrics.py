#!/usr/bin/env python3
"""
Convenience script to visualize all metrics for both question_type and dimension using radar plots.
"""
import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def plot_llm_metrics(df, category_col, out_dir, figsize):
    """
    Plot LLM-related metrics as radar plot: Mem_helpful_score_norm_mean, Mem_recall_norm_mean, 
    QA_consistency_score_norm_mean, choice_accuracy_mean, qa_hallucination_rate_mean, qa_perfect_rate_mean
    Each category (question_type/dimension) becomes an axis on the radar plot.
    Each metric becomes a separate line/polygon.
    """
    metrics = [
        'Mem_helpful_score_norm_mean',
        'Mem_recall_norm_mean', 
        'QA_consistency_score_norm_mean',
        'choice_accuracy_mean',
        'qa_hallucination_rate_mean',
        'qa_perfect_rate_mean'
    ]
    
    metric_labels = {
        'Mem_helpful_score_norm_mean': 'Mem Helpful Score',
        'Mem_recall_norm_mean': 'Mem Recall',
        'QA_consistency_score_norm_mean': 'QA Consistency',
        'choice_accuracy_mean': 'Choice Accuracy',
        'qa_hallucination_rate_mean': 'Non-Halluc.',
        'qa_perfect_rate_mean': 'Perfect Rate'
    }
    
    # Check which metrics are available
    available_metrics = [m for m in metrics if m in df.columns]
    
    if not available_metrics:
        print(f"Warning: No LLM metrics found in the CSV file")
        return
    
    # Prepare data - invert qa_hallucination_rate to make it Non-Hallucination rate
    categories = df[category_col].values.tolist()
    n_categories = len(categories)
    
    # Set up radar plot
    angles = np.linspace(0, 2 * np.pi, n_categories, endpoint=False).tolist()
    angles += angles[:1]  # Complete the circle
    
    # Create figure with polar projection
    fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(projection='polar'))
    
    # Color palette and line styles
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#06A77D', '#E63946', '#8338EC']
    markers = ['o', 's', '^', 'D', 'v', 'p']
    linestyles = ['-', '--', '-.', ':', '-', '--']
    
    # Plot each metric
    for i, metric in enumerate(available_metrics):
        values = df[metric].values.tolist()
        
        # Invert hallucination rate to show non-hallucination rate
        if metric == 'qa_hallucination_rate_mean':
            values = [1 - v for v in values]
        
        values += values[:1]  # Complete the circle
        
        ax.plot(angles, values, linewidth=2.5, 
               label=metric_labels.get(metric, metric),
               color=colors[i % len(colors)],
               marker=markers[i % len(markers)],
               markersize=8,
               linestyle=linestyles[i % len(linestyles)])
        ax.fill(angles, values, alpha=0.1, color=colors[i % len(colors)])
    
    # Customize plot
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=16)
    ax.set_ylim(0, 1.0)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=10)
    # ax.set_title(f'LLM Metrics by {category_col.replace("_", " ").title()}', 
    #             fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), frameon=True, shadow=False, fontsize=14, ncol=3)
    ax.grid(True, alpha=0.7, linestyle='--')
    
    # Tight layout
    plt.tight_layout()
    
    # Save figure
    output_file = os.path.join(out_dir, f'llm_metrics_by_{category_col}_radar.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved LLM metrics radar chart to: {output_file}")
    
    # Also save as PDF
    output_pdf = os.path.join(out_dir, f'llm_metrics_by_{category_col}_radar.pdf')
    plt.savefig(output_pdf, bbox_inches='tight')
    print(f"Saved LLM metrics radar chart to: {output_pdf}")
    
    plt.close()


def plot_recall_metrics(df, category_col, out_dir, figsize):
    """
    Plot recall metrics as radar plot: recall_all_all_k10_mean, recall_all_any_k10_mean, 
    recall_any_any_k10_mean, recall_flat_k10_mean
    Each category (question_type/dimension) becomes an axis on the radar plot.
    Each metric becomes a separate line/polygon.
    """
    metrics = [
        'recall_all_all_k10_mean',
        'recall_all_any_k10_mean',
        'recall_any_any_k10_mean',
        'recall_flat_k10_mean'
    ]
    
    metric_labels = {
        'recall_all_all_k10_mean': 'Recall All-All @10',
        'recall_all_any_k10_mean': 'Recall All-Any @10',
        'recall_any_any_k10_mean': 'Recall Any-Any @10',
        'recall_flat_k10_mean': 'Recall Flat @10'
    }
    
    # Check which metrics are available
    available_metrics = [m for m in metrics if m in df.columns]
    
    if not available_metrics:
        print(f"Warning: No recall metrics found in the CSV file")
        return
    
    # Prepare data
    categories = df[category_col].values.tolist()
    n_categories = len(categories)
    
    # Set up radar plot
    angles = np.linspace(0, 2 * np.pi, n_categories, endpoint=False).tolist()
    angles += angles[:1]  # Complete the circle
    
    # Create figure with polar projection
    fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(projection='polar'))
    
    # Color palette and line styles
    colors = ['#E63946', '#457B9D', '#2A9D8F', '#F77F00']
    markers = ['o', 's', '^', 'D']
    linestyles = ['-', '--', '-.', ':']
    
    # Find max value for scaling
    max_val = df[available_metrics].max().max()
    # y_max = max(1.0, np.ceil(max_val * 10) / 10)  # Round up to nearest 0.1
    y_max=0.6
    
    # Plot each metric
    for i, metric in enumerate(available_metrics):
        values = df[metric].values.tolist()
        values += values[:1]  # Complete the circle
        
        ax.plot(angles, values, linewidth=2.5,
               label=metric_labels.get(metric, metric),
               color=colors[i % len(colors)],
               marker=markers[i % len(markers)],
               markersize=8,
               linestyle=linestyles[i % len(linestyles)])
        ax.fill(angles, values, alpha=0.1, color=colors[i % len(colors)])
    
    # Customize plot
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=16)
    ax.set_ylim(0, y_max)
    
    # Set appropriate y-ticks based on scale
    if y_max <= 1.0:
        # yticks = [0.2, 0.4, 0.6, 0.8, 1.0]
        yticks = [0.2, 0.4, 0.6, 0.7]
        yticklabels = [f'{y:.1f}' for y in yticks]
    else:
        yticks = np.linspace(0, y_max, 6)[1:]  # 5 tick marks
        yticklabels = [f'{y:.2f}' for y in yticks]
    
    ax.set_yticks(yticks)
    ax.set_yticklabels(yticklabels, fontsize=10)
    # ax.set_title(f'Recall Metrics @k=10 by {category_col.replace("_", " ").title()}',
    #             fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), frameon=True, shadow=False, fontsize=14, ncol=2)
    ax.grid(True, alpha=0.7, linestyle='--')
    
    # Tight layout
    plt.tight_layout()
    
    # Save figure
    output_file = os.path.join(out_dir, f'recall_metrics_by_{category_col}_radar.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved recall metrics radar chart to: {output_file}")
    
    # Also save as PDF
    output_pdf = os.path.join(out_dir, f'recall_metrics_by_{category_col}_radar.pdf')
    plt.savefig(output_pdf, bbox_inches='tight')
    print(f"Saved recall metrics radar chart to: {output_pdf}")
    
    plt.close()


def parse_args():
    parser = argparse.ArgumentParser(description="Visualize all aggregated metrics using radar plots")
    parser.add_argument('--aggregated_dir', type=str,
                        default='checkpoints/new_data/flatten/aggregated_analysis',
                        help='Directory containing aggregated CSV files')
    parser.add_argument('--figsize', type=int, nargs=2, default=[10, 10],
                        help='Figure size (width height)')
    return parser.parse_args()


def main(args):
    print("=" * 60)
    print("Visualizing All Aggregated Metrics (Radar Plots)")
    print("=" * 60)
    
    # Define the files to process
    files_to_process = [
        ('metrics_by_question_type.csv', 'question_type'),
        ('metrics_by_dimension.csv', 'dimension')
    ]
    
    for filename, category_col in files_to_process:
        csv_file = os.path.join(args.aggregated_dir, filename)
        
        if not os.path.exists(csv_file):
            print(f"\nWarning: File not found: {csv_file}")
            continue
        
        print(f"\n{'=' * 60}")
        print(f"Processing: {filename}")
        print(f"Category: {category_col}")
        print('=' * 60)
        
        # Load data
        df = pd.read_csv(csv_file)
        print(f"Loaded {len(df)} rows")
        print(f"Categories: {df[category_col].tolist()}")
        
        # Plot LLM metrics
        print(f"\nPlotting LLM metrics...")
        plot_llm_metrics(df, category_col, args.aggregated_dir, tuple(args.figsize))
        
        # Plot recall metrics
        print(f"Plotting recall metrics...")
        plot_recall_metrics(df, category_col, args.aggregated_dir, tuple(args.figsize))
    
    print("\n" + "=" * 60)
    print("All Visualizations Complete!")
    print(f"Charts saved to: {args.aggregated_dir}")
    print("=" * 60)


if __name__ == "__main__":
    args = parse_args()
    main(args)
