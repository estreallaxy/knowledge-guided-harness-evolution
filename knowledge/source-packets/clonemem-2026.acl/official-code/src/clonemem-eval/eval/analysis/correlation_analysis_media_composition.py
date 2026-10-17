import json
import argparse
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import pearsonr
from collections import defaultdict
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = os.path.expanduser("~/playground/AgentMem/clonemem_adaptation")
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def parse_args():
    parser = argparse.ArgumentParser(description="Correlation analysis between media composition and LLM metrics")
    parser.add_argument('--input_file', type=str,
                        default='checkpoints/new_data/amem/generation_results/media_composition_analysis/media_composition_impact_per_question.json',
                        help='Input JSON file with media composition data per question')
    parser.add_argument('--out_dir', type=str, default=None,
                        help='Output directory to save analysis results')
    parser.add_argument('--dominance_threshold', type=float, default=0.4,
                        help='Threshold for considering a media type as dominant (default: 0.4 = 40%%)')
    parser.add_argument('--min_samples', type=int, default=10,
                        help='Minimum number of samples required for stratified analysis')
    parser.add_argument('--min_effect_size', type=float, default=0.2,
                        help='Minimum absolute correlation coefficient to mark as significant (default: 0.2, Cohen\'s small-to-medium)')
    return parser.parse_args()


def load_data(input_file):
    """Load media composition data."""
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def consolidate_media_types(media_type):
    """
    Consolidate similar media types into broader categories.
    
    Categories:
    - chat_private: message, sms, call_log
    - diary: note, diary
    - memo: memo, todo
    - calendar_event: calendar_event
    - search_history: search_history, browser_history
    - wechat_moments: wechat_moment, social_media_post
    - work_log: work_log
    - others: everything else
    """
    media_type_lower = media_type.lower()
    
    # Chat private: one-on-one communications
    if media_type_lower in ['message', 'sms', 'call_log']:
        return 'chat_private'
    
    # Diary: personal reflections
    elif media_type_lower in ['note', 'diary']:
        return 'diary'
    
    # Memo: tasks and reminders
    elif media_type_lower in ['memo', 'todo']:
        return 'memo'
    
    # Calendar event
    elif media_type_lower in ['calendar_event']:
        return 'calendar_event'
    
    # Search history: browsing activities
    elif media_type_lower in ['search_history', 'browser_history']:
        return 'search_history'
    
    # WeChat moments: social media
    elif media_type_lower in ['wechat_moment', 'social_media_post']:
        return 'wechat_moments'
    
    # Work log
    elif media_type_lower in ['work_log']:
        return 'work_log'
    
    # Others: everything else
    else:
        return 'others'


def prepare_dataframe(data):
    """
    Convert raw data to a pandas DataFrame suitable for analysis.
    """
    rows = []
    
    for item in data:
        row = {
            'question_id': item['question_id'],
            'user_id': item['user_id'],
            'person_name': item['person_name'],
            'question_type': item['question_type'],
            'dimension': item['dimension'],
            'num_contexts': item['num_contexts_before_question'],
            # Performance metrics
            'QA_consistency_score': item['QA_consistency_score'],
            'Mem_recall': item['Mem_recall'],
            'Mem_helpful_score': item['Mem_helpful_score'],
        }
        
        # Add normalized scores
        row['QA_consistency_score_norm'] = item['QA_consistency_score'] / 3.0
        row['Mem_helpful_score_norm'] = item['Mem_helpful_score'] / 2.0
        
        # Consolidate media types and aggregate percentages
        consolidated_pct = defaultdict(float)
        consolidated_count = defaultdict(int)
        
        for media_type, percentage in item['media_composition_percentages'].items():
            consolidated_type = consolidate_media_types(media_type)
            consolidated_pct[consolidated_type] += percentage
        
        for media_type, count in item['media_composition_counts'].items():
            consolidated_type = consolidate_media_types(media_type)
            consolidated_count[consolidated_type] += count
        
        # Add consolidated media percentages and counts
        for media_type, percentage in consolidated_pct.items():
            row[f'media_{media_type}_pct'] = percentage
        
        for media_type, count in consolidated_count.items():
            row[f'media_{media_type}_count'] = count
        
        rows.append(row)
    
    df = pd.DataFrame(rows)
    
    # Fill NaN with 0 for media types not present
    media_cols = [col for col in df.columns if col.startswith('media_')]
    df[media_cols] = df[media_cols].fillna(0)
    
    return df


def compute_correlations(df, media_cols, metric_cols, method='pearson'):
    """
    Compute correlations between media type percentages and performance metrics.
    
    Returns:
        - correlation_matrix: DataFrame with correlation coefficients
        - pvalue_matrix: DataFrame with p-values
    """
    corr_results = {}
    pval_results = {}
    
    for media_col in media_cols:
        corr_results[media_col] = {}
        pval_results[media_col] = {}
        
        for metric_col in metric_cols:
            # Remove NaN values
            valid_mask = df[[media_col, metric_col]].notna().all(axis=1)
            x = df.loc[valid_mask, media_col]
            y = df.loc[valid_mask, metric_col]
            
            if len(x) < 3:  # Need at least 3 points for correlation
                corr_results[media_col][metric_col] = np.nan
                pval_results[media_col][metric_col] = np.nan
                continue
            
            if method == 'pearson':
                corr, pval = pearsonr(x, y)
            elif method == 'spearman':
                corr, pval = spearmanr(x, y)
            else:
                raise ValueError(f"Unknown correlation method: {method}")
            
            corr_results[media_col][metric_col] = corr
            pval_results[media_col][metric_col] = pval
    
    corr_df = pd.DataFrame(corr_results).T
    pval_df = pd.DataFrame(pval_results).T
    
    return corr_df, pval_df


def stratified_correlation_analysis(df, media_cols, metric_cols, stratify_by, min_samples=10):
    """
    Perform correlation analysis stratified by a categorical variable.
    """
    results = {}
    
    for category in df[stratify_by].unique():
        subset = df[df[stratify_by] == category]
        
        if len(subset) < min_samples:
            print(f"  ⚠️  Skipping {stratify_by}='{category}': only {len(subset)} samples (min: {min_samples})")
            continue
        
        print(f"  Analyzing {stratify_by}='{category}' ({len(subset)} samples)")
        
        # Compute correlations for this subset
        pearson_corr, pearson_pval = compute_correlations(subset, media_cols, metric_cols, method='pearson')
        
        results[category] = {
            'n_samples': len(subset),
            'pearson_corr': pearson_corr,
            'pearson_pval': pearson_pval,
        }
    
    return results


def dominant_media_analysis(df, media_pct_cols, metric_cols, threshold=0.4):
    """
    Identify dominant media type for each question and compare metrics.
    """
    # Find dominant media type for each question
    media_types = [col.replace('media_', '').replace('_pct', '') for col in media_pct_cols]
    
    def get_dominant_media(row):
        """Get the dominant media type (if any exceeds threshold)."""
        max_pct = 0
        dominant = 'mixed'
        
        for col in media_pct_cols:
            if row[col] > max_pct:
                max_pct = row[col]
                dominant = col.replace('media_', '').replace('_pct', '')
        
        # Only consider it dominant if it exceeds threshold
        if max_pct < threshold * 100:  # threshold is in decimal, percentages are 0-100
            dominant = 'mixed'
        
        return dominant
    
    df['dominant_media'] = df.apply(get_dominant_media, axis=1)
    
    # Compute statistics for each dominant media group
    results = {}
    
    for media_type in df['dominant_media'].unique():
        subset = df[df['dominant_media'] == media_type]
        
        if len(subset) < 3:
            continue
        
        stats_dict = {
            'n_samples': len(subset),
            'metrics': {}
        }
        
        for metric in metric_cols:
            stats_dict['metrics'][metric] = {
                'mean': subset[metric].mean(),
                'std': subset[metric].std(),
                'median': subset[metric].median(),
                'min': subset[metric].min(),
                'max': subset[metric].max(),
            }
        
        results[media_type] = stats_dict
    
    return results, df


def bonferroni_correction(pval_df, n_comparisons=None):
    """
    Apply Bonferroni correction to p-values.
    """
    if n_comparisons is None:
        n_comparisons = pval_df.size
    
    corrected = pval_df * n_comparisons
    corrected = corrected.clip(upper=1.0)  # P-values can't exceed 1
    
    return corrected


def plot_correlation_heatmap(corr_df, pval_df, title, output_path, figsize=(12, 10), 
                            min_effect_size=0.2, pval_corrected_df=None):
    """
    Plot correlation heatmap with significance markers.
    
    Args:
        corr_df: Correlation coefficients
        pval_df: P-values (will be used if pval_corrected_df is None)
        title: Plot title
        output_path: Output file path
        figsize: Figure size
        min_effect_size: Minimum absolute correlation to consider meaningful (default: 0.2)
        pval_corrected_df: Bonferroni-corrected p-values (preferred for significance markers)
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Use corrected p-values if provided, otherwise use uncorrected
    pval_for_stars = pval_corrected_df if pval_corrected_df is not None else pval_df
    
    # Create annotation matrix with correlations and significance stars
    annot = corr_df.copy()
    for i in range(len(corr_df)):
        for j in range(len(corr_df.columns)):
            corr_val = corr_df.iloc[i, j]
            pval = pval_for_stars.iloc[i, j]
            
            if pd.isna(corr_val):
                annot.iloc[i, j] = ''
            else:
                # Add significance stars ONLY if both statistically significant AND meaningful effect size
                stars = ''
                abs_corr = abs(corr_val)
                
                # Require BOTH: p-value significance AND minimum effect size
                if abs_corr >= min_effect_size:
                    if pval < 0.001:
                        stars = '***'
                    elif pval < 0.01:
                        stars = '**'
                    elif pval < 0.05:
                        stars = '*'
                
                annot.iloc[i, j] = f'{corr_val:.3f}{stars}'
    
    # Plot heatmap
    sns.heatmap(corr_df, annot=annot, fmt='', cmap='RdBu_r', center=0,
                vmin=-1, vmax=1, cbar_kws={'label': 'Correlation'},
                ax=ax, linewidths=0.5)
    
    # Add subtitle explaining significance criteria
    subtitle = f'* p<0.05, ** p<0.01, *** p<0.001 (Bonferroni corrected) AND |r|≥{min_effect_size}'
    ax.set_title(f'{title}\n{subtitle}', fontsize=14, fontweight='bold')
    ax.set_xlabel('Performance Metrics', fontsize=12)
    ax.set_ylabel('Media Type', fontsize=12)
    
    # Rotate labels
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Saved heatmap to: {output_path}")


def plot_scatter_top_correlations(df, media_cols, metric_cols, corr_df, pval_df, 
                                   output_dir, top_k=6, alpha=0.05, min_effect_size=0.2,
                                   pval_corrected_df=None):
    """
    Plot scatter plots for top correlations.
    
    Args:
        min_effect_size: Minimum absolute correlation to consider (default: 0.2)
        pval_corrected_df: Bonferroni-corrected p-values (if None, uses uncorrected)
    """
    # Use corrected p-values if provided
    pval_for_filtering = pval_corrected_df if pval_corrected_df is not None else pval_df
    
    # Flatten correlation matrix and sort by absolute value
    corr_flat = []
    for media_col in corr_df.index:
        for metric_col in corr_df.columns:
            corr_val = corr_df.loc[media_col, metric_col]
            pval = pval_for_filtering.loc[media_col, metric_col]
            
            # Require BOTH significance AND meaningful effect size
            if not pd.isna(corr_val) and pval < alpha and abs(corr_val) >= min_effect_size:
                corr_flat.append({
                    'media': media_col,
                    'metric': metric_col,
                    'correlation': corr_val,
                    'pvalue': pval,
                    'abs_corr': abs(corr_val)
                })
    
    # Sort by absolute correlation
    corr_flat = sorted(corr_flat, key=lambda x: x['abs_corr'], reverse=True)
    
    if not corr_flat:
        print(f"  ⚠️  No significant correlations found with |r|≥{min_effect_size} (try lowering min_effect_size)")
        return
    
    # Plot top K
    top_corrs = corr_flat[:top_k]
    
    n_plots = len(top_corrs)
    n_cols = 3
    n_rows = (n_plots + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5 * n_rows))
    axes = axes.flatten() if n_plots > 1 else [axes]
    
    for idx, item in enumerate(top_corrs):
        ax = axes[idx]
        
        media_col = item['media']
        metric_col = item['metric']
        corr = item['correlation']
        pval = item['pvalue']
        
        # Extract data
        valid_mask = df[[media_col, metric_col]].notna().all(axis=1)
        x = df.loc[valid_mask, media_col]
        y = df.loc[valid_mask, metric_col]
        
        # Scatter plot
        ax.scatter(x, y, alpha=0.5, s=30)
        
        # Add regression line
        if len(x) > 1:
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            x_line = np.linspace(x.min(), x.max(), 100)
            ax.plot(x_line, p(x_line), 'r--', alpha=0.8, linewidth=2)
        
        # Labels
        media_name = media_col.replace('media_', '').replace('_pct', '')
        ax.set_xlabel(f'{media_name} (%)', fontsize=10)
        ax.set_ylabel(metric_col.replace('_', ' ').title(), fontsize=10)
        ax.set_title(f'r={corr:.3f}, p={pval:.4f}', fontsize=11, fontweight='bold')
        ax.grid(True, alpha=0.3)
    
    # Hide empty subplots
    for idx in range(n_plots, len(axes)):
        axes[idx].axis('off')
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'top_correlations_scatter.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Saved scatter plots to: {output_path}")


def plot_dominant_media_comparison(df, metric_cols, output_dir):
    """
    Plot box plots comparing metrics across dominant media types.
    """
    # Filter out groups with too few samples
    media_counts = df['dominant_media'].value_counts()
    valid_media = media_counts[media_counts >= 5].index.tolist()
    
    if len(valid_media) < 2:
        print("  ⚠️  Not enough dominant media groups for comparison")
        return
    
    df_filtered = df[df['dominant_media'].isin(valid_media)]
    
    n_metrics = len(metric_cols)
    n_cols = 2
    n_rows = (n_metrics + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(14, 5 * n_rows))
    axes = axes.flatten() if n_metrics > 1 else [axes]
    
    for idx, metric in enumerate(metric_cols):
        ax = axes[idx]
        
        # Box plot
        df_filtered.boxplot(column=metric, by='dominant_media', ax=ax)
        
        ax.set_xlabel('Dominant Media Type', fontsize=11)
        ax.set_ylabel(metric.replace('_', ' ').title(), fontsize=11)
        ax.set_title(f'{metric.replace("_", " ").title()} by Dominant Media', fontsize=12, fontweight='bold')
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Remove the automatic title from boxplot
        ax.get_figure().suptitle('')
    
    # Hide empty subplots
    for idx in range(n_metrics, len(axes)):
        axes[idx].axis('off')
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'dominant_media_comparison.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Saved dominant media comparison to: {output_path}")


def export_results_to_json(results, output_path):
    """
    Export results to JSON file, converting DataFrames to dicts.
    """
    def convert_to_serializable(obj):
        """Convert DataFrames and numpy types to JSON-serializable format."""
        if isinstance(obj, pd.DataFrame):
            return obj.to_dict()
        elif isinstance(obj, pd.Series):
            return obj.to_dict()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_serializable(item) for item in obj]
        else:
            return obj
    
    serializable_results = convert_to_serializable(results)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(serializable_results, f, ensure_ascii=False, indent=2)
    
    print(f"  ✓ Saved results to: {output_path}")


def main(args):
    print("=" * 80)
    print("Correlation Analysis: Media Composition vs LLM Performance Metrics")
    print("=" * 80)
    
    # Load data
    print(f"\nLoading data from: {args.input_file}")
    data = load_data(args.input_file)
    print(f"Loaded {len(data)} questions")
    
    # Prepare DataFrame
    print("\nPreparing data...")
    df = prepare_dataframe(data)
    print(f"DataFrame shape: {df.shape}")
    
    # Identify media columns and metric columns
    media_pct_cols = [col for col in df.columns if col.startswith('media_') and col.endswith('_pct')]
    media_count_cols = [col for col in df.columns if col.startswith('media_') and col.endswith('_count')]
    
    metric_cols = [
        'QA_consistency_score',
        'QA_consistency_score_norm',
        'Mem_recall',
        'Mem_helpful_score',
        'Mem_helpful_score_norm'
    ]
    
    print(f"\nFound {len(media_pct_cols)} media types (percentage)")
    print(f"Analyzing {len(metric_cols)} performance metrics")
    
    # Set output directory
    if not args.out_dir:
        args.out_dir = os.path.dirname(args.input_file)
    
    os.makedirs(args.out_dir, exist_ok=True)
    print(f"\nOutput directory: {args.out_dir}")
    
    # =========================================================================
    # 1. Overall Correlation Analysis
    # =========================================================================
    print("\n" + "=" * 80)
    print("1. Overall Correlation Analysis (Pearson)")
    print("=" * 80)
    
    pearson_corr, pearson_pval = compute_correlations(df, media_pct_cols, metric_cols, method='pearson')
    
    print("\nPearson Correlations:")
    print(pearson_corr)
    
    # Apply Bonferroni correction
    n_tests = pearson_pval.size
    pearson_pval_corrected = bonferroni_correction(pearson_pval, n_tests)
    
    print(f"\nNumber of statistical tests: {n_tests}")
    print(f"Bonferroni-corrected significance threshold: {0.05 / n_tests:.6f}")
    print(f"Minimum effect size threshold: |r| ≥ {args.min_effect_size}")
    
    # Plot heatmap WITH corrected p-values and effect size threshold
    plot_correlation_heatmap(
        pearson_corr, pearson_pval,
        'Pearson Correlation: Media Composition vs Performance Metrics',
        os.path.join(args.out_dir, 'correlation_heatmap_pearson.png'),
        min_effect_size=args.min_effect_size,
        pval_corrected_df=pearson_pval_corrected
    )
    
    # Plot scatter plots for top correlations WITH corrected p-values
    plot_scatter_top_correlations(
        df, media_pct_cols, metric_cols, pearson_corr, pearson_pval,
        args.out_dir, top_k=6, alpha=0.05, min_effect_size=args.min_effect_size,
        pval_corrected_df=pearson_pval_corrected
    )
    
    # =========================================================================
    # 2. Stratified Analysis by Question Type
    # =========================================================================
    print("\n" + "=" * 80)
    print("2. Stratified Analysis by Question Type")
    print("=" * 80)
    
    question_type_results = stratified_correlation_analysis(
        df, media_pct_cols, metric_cols, 'question_type', min_samples=args.min_samples
    )
    
    # =========================================================================
    # 3. Stratified Analysis by Dimension
    # =========================================================================
    print("\n" + "=" * 80)
    print("3. Stratified Analysis by Dimension")
    print("=" * 80)
    
    dimension_results = stratified_correlation_analysis(
        df, media_pct_cols, metric_cols, 'dimension', min_samples=args.min_samples
    )
    
    # =========================================================================
    # 4. Dominant Media Type Analysis
    # =========================================================================
    print("\n" + "=" * 80)
    print("4. Dominant Media Type Analysis")
    print("=" * 80)
    print(f"Dominance threshold: {args.dominance_threshold * 100}%")
    
    dominant_results, df = dominant_media_analysis(
        df, media_pct_cols, metric_cols, threshold=args.dominance_threshold
    )
    
    print("\nDominant media type distribution:")
    print(df['dominant_media'].value_counts())
    
    print("\nPerformance by dominant media type:")
    for media_type, stats in dominant_results.items():
        print(f"\n  {media_type} (n={stats['n_samples']}):")
        for metric, values in stats['metrics'].items():
            print(f"    {metric}: mean={values['mean']:.3f}, std={values['std']:.3f}")
    
    # Plot comparison
    plot_dominant_media_comparison(df, metric_cols, args.out_dir)
    
    # =========================================================================
    # 5. Context Volume Correlation
    # =========================================================================
    print("\n" + "=" * 80)
    print("5. Context Volume Correlation Analysis")
    print("=" * 80)
    
    volume_corr = {}
    for metric in metric_cols:
        valid_mask = df[['num_contexts', metric]].notna().all(axis=1)
        x = df.loc[valid_mask, 'num_contexts']
        y = df.loc[valid_mask, metric]
        
        pearson_r, pearson_p = pearsonr(x, y)
        
        volume_corr[metric] = {
            'pearson_r': pearson_r,
            'pearson_p': pearson_p,
        }
        
        print(f"{metric}:")
        print(f"  Pearson:  r={pearson_r:.3f}, p={pearson_p:.4f}")
    
    # =========================================================================
    # 6. Export All Results
    # =========================================================================
    print("\n" + "=" * 80)
    print("6. Exporting Results")
    print("=" * 80)
    
    all_results = {
        'overall': {
            'pearson_correlation': pearson_corr.to_dict(),
            'pearson_pvalue': pearson_pval.to_dict(),
            'pearson_pvalue_bonferroni': pearson_pval_corrected.to_dict(),
            'n_tests': n_tests,
        },
        'stratified_by_question_type': question_type_results,
        'stratified_by_dimension': dimension_results,
        'dominant_media_analysis': dominant_results,
        'context_volume_correlation': volume_corr,
        'parameters': {
            'dominance_threshold': args.dominance_threshold,
            'min_samples': args.min_samples,
            'min_effect_size': args.min_effect_size,
            'n_total_questions': len(df),
        }
    }
    
    export_results_to_json(
        all_results,
        os.path.join(args.out_dir, 'correlation_analysis_results.json')
    )
    
    # Export summary CSV files
    pearson_corr.to_csv(os.path.join(args.out_dir, 'pearson_correlations.csv'))
    print(f"  ✓ Saved correlation CSV")
    
    # Export processed DataFrame
    df.to_csv(os.path.join(args.out_dir, 'processed_data_with_dominant_media.csv'), index=False)
    print(f"  ✓ Saved processed data with dominant media labels")
    
    print("\n" + "=" * 80)
    print("Analysis Complete!")
    print("=" * 80)
    
    # Print key findings with PROPER significance interpretation
    print("\n📊 KEY FINDINGS:")
    print("-" * 80)
    print(f"\n⚠️  IMPORTANT: With {len(df)} samples and {n_tests} tests:")
    print(f"   • Bonferroni-corrected alpha: {0.05 / n_tests:.6f}")
    print(f"   • Minimum effect size for marking: |r| ≥ {args.min_effect_size}")
    print(f"   • Small correlations (|r|<{args.min_effect_size}) are NOT marked, even if p<0.05")
    print(f"\n   Effect Size Guidelines (Cohen's):")
    print(f"   • |r| ≥ 0.1: Small effect (explains ≥1% variance)")
    print(f"   • |r| ≥ 0.3: Medium effect (explains ≥9% variance)")
    print(f"   • |r| ≥ 0.5: Large effect (explains ≥25% variance)")
    
    # Find strongest correlations WITH Bonferroni correction AND effect size
    print(f"\n1. Meaningful Positive Correlations (Bonferroni p<0.05, |r|≥{args.min_effect_size}):")
    strong_pos = []
    for media in pearson_corr.index:
        for metric in pearson_corr.columns:
            corr = pearson_corr.loc[media, metric]
            pval = pearson_pval_corrected.loc[media, metric]
            if not pd.isna(corr) and corr >= args.min_effect_size and pval < 0.05:
                r_squared = corr ** 2
                strong_pos.append((media, metric, corr, pval, r_squared))
    
    strong_pos.sort(key=lambda x: x[2], reverse=True)
    if strong_pos:
        for media, metric, corr, pval, r_sq in strong_pos[:10]:
            media_name = media.replace('media_', '').replace('_pct', '')
            print(f"  • {media_name:20s} → {metric:30s}  r={corr:6.3f}  p={pval:.6f}  (R²={r_sq:.3f}, explains {r_sq*100:.1f}% variance)")
    else:
        print("  ⚠️  No meaningful positive correlations found after correction")
    
    print(f"\n2. Meaningful Negative Correlations (Bonferroni p<0.05, |r|≥{args.min_effect_size}):")
    strong_neg = []
    for media in pearson_corr.index:
        for metric in pearson_corr.columns:
            corr = pearson_corr.loc[media, metric]
            pval = pearson_pval_corrected.loc[media, metric]
            if not pd.isna(corr) and corr <= -args.min_effect_size and pval < 0.05:
                r_squared = corr ** 2
                strong_neg.append((media, metric, corr, pval, r_squared))
    
    strong_neg.sort(key=lambda x: x[2])
    if strong_neg:
        for media, metric, corr, pval, r_sq in strong_neg[:10]:
            media_name = media.replace('media_', '').replace('_pct', '')
            print(f"  • {media_name:20s} → {metric:30s}  r={corr:6.3f}  p={pval:.6f}  (R²={r_sq:.3f}, explains {r_sq*100:.1f}% variance)")
    else:
        print("  ⚠️  No meaningful negative correlations found after correction")
    
    # Show weak but statistically significant correlations (for transparency)
    print(f"\n3. Statistically Significant but WEAK Correlations (Bonferroni p<0.05, |r|<{args.min_effect_size}):")
    print("   (These are marked in results but NOT in visualizations due to low practical significance)")
    weak_sig = []
    for media in pearson_corr.index:
        for metric in pearson_corr.columns:
            corr = pearson_corr.loc[media, metric]
            pval = pearson_pval_corrected.loc[media, metric]
            if not pd.isna(corr) and abs(corr) < args.min_effect_size and pval < 0.05:
                weak_sig.append((media, metric, corr, pval))
    
    if weak_sig:
        weak_sig.sort(key=lambda x: abs(x[2]), reverse=True)
        for media, metric, corr, pval in weak_sig[:5]:
            media_name = media.replace('media_', '').replace('_pct', '')
            print(f"  • {media_name:20s} → {metric:30s}  r={corr:6.3f}  p={pval:.6f}  (too weak to interpret)")
    else:
        print("  ✓ No weak correlations found")

    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    args = parse_args()
    main(args)
