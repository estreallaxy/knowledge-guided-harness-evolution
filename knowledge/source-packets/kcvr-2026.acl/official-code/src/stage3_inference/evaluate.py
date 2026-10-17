#!/usr/bin/env python3
# Evaluation script: compute all metrics (ROUGE, BERTScore, C-F1, KPC, LOC)

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List
from collections import defaultdict

# Add project root to path
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.evaluation.eval_main import (
    load_predictions,
    load_ground_truth,
    load_plan,
    compute_all_metrics,
    load_ctl_resources,
    load_kg_edges,
    macro_average_across_subjects
)
from src.utils.metric_utils import CtlResources, KgEdges

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def evaluate_predictions(predictions_file: Path, labels_root: Path, plans_root: Path,
                        kg_csv_root: Path, output_dir: Path, level: str = 'micro') -> None:
    # Evaluate predictions and compute metrics
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load resources
    logger.info("Loading resources...")
    ctl_resources = load_ctl_resources(kg_csv_root)
    kg_edges = load_kg_edges(kg_csv_root)
    
    # Load predictions
    logger.info("Loading predictions...")
    predictions = load_predictions(predictions_file)
    logger.info(f"Loaded {len(predictions)} predictions")
    
    # Load ground truth and compute metrics
    logger.info("Computing metrics...")
    results = []
    
    for pred in predictions:
        subject = pred.get('subject', '')
        video_id = pred.get('video_id', '')
        segment_id = pred.get('segment_id', '')
        
        # Load ground truth
        if level == 'micro':
            label_path = labels_root / subject / f"{video_id}__{segment_id}.json"
        else:
            label_path = labels_root / subject / f"{video_id}_global.json"
        
        if not label_path.exists():
            logger.warning(f"Label not found: {label_path}")
            continue
        
        gt = json.load(open(label_path, 'r', encoding='utf-8'))
        
        # Load plan
        if level == 'micro':
            plan = load_plan(plans_root, subject, video_id, segment_id)
        else:
            # For macro, plan might be GKS
            plan = None  # Simplified - should load GKS
        
        if not plan and level == 'micro':
            logger.warning(f"Plan not found for {subject}/{video_id}/{segment_id}")
            continue
        
        # Extract texts
        pred_summary = pred.get('summary', '')
        pred_objectives = pred.get('objectives', '')
        gt_summary = gt.get('summary_gt', '') or gt.get('summary', '')
        gt_objectives = gt.get('objectives_gt', '') or gt.get('objectives', '')
        
        # Extract plan information
        plan_pi_kc = plan.get('pi', []) if plan else []
        plan_edges_based_on = plan.get('edges_based_on', []) if plan else []
        plan_edges_next = plan.get('edges_next', []) if plan else []
        
        # Compute metrics
        try:
            metrics = compute_all_metrics(
                pred_text=pred_summary,
                ref_text=gt_summary,
                pred_objectives=pred_objectives,
                gold_objectives=gt_objectives,
                plan_pi_kc=plan_pi_kc,
                plan_edges_based_on=plan_edges_based_on,
                plan_edges_next=plan_edges_next,
                subject=subject,
                ctl_resources=ctl_resources
            )
            
            result = {
                'subject': subject,
                'video_id': video_id,
                'segment_id': segment_id if level == 'micro' else 'global',
                **metrics
            }
            results.append(result)
            
        except Exception as e:
            logger.error(f"Error computing metrics for {subject}/{video_id}/{segment_id}: {e}")
            continue
    
    # Compute macro averages
    logger.info("Computing macro averages...")
    macro_avg = macro_average_across_subjects(results)
    
    # Save results
    results_file = output_dir / 'metrics_detailed.json'
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    summary_file = output_dir / 'metrics_summary.json'
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump({
            'macro_average': macro_avg,
            'num_samples': len(results)
        }, f, indent=2, ensure_ascii=False)
    
    # Print summary
    logger.info("\n=== Evaluation Results ===")
    logger.info(f"Number of samples: {len(results)}")
    logger.info("\nMacro Average Metrics:")
    for metric, value in macro_avg.items():
        logger.info(f"  {metric}: {value:.4f}")
    
    logger.info(f"\nResults saved to:")
    logger.info(f"  Detailed: {results_file}")
    logger.info(f"  Summary: {summary_file}")


def main():
    parser = argparse.ArgumentParser(description="KCVR Evaluation")
    parser.add_argument('--predictions', type=str, required=True,
                       help='Path to predictions JSONL file')
    parser.add_argument('--labels-root', type=str, required=True,
                       help='Root directory for ground truth labels')
    parser.add_argument('--plans-root', type=str, required=True,
                       help='Root directory for plans')
    parser.add_argument('--kg-csv-root', type=str, required=True,
                       help='Root directory for KG CSV files')
    parser.add_argument('--output-dir', type=str, required=True,
                       help='Output directory for metrics')
    parser.add_argument('--level', type=str, default='micro',
                       choices=['micro', 'macro'],
                       help='Evaluation level')
    
    args = parser.parse_args()
    
    # Convert to Path objects
    predictions_file = Path(args.predictions)
    labels_root = Path(args.labels_root)
    plans_root = Path(args.plans_root)
    kg_csv_root = Path(args.kg_csv_root)
    output_dir = Path(args.output_dir)
    
    # Run evaluation
    evaluate_predictions(
        predictions_file=predictions_file,
        labels_root=labels_root,
        plans_root=plans_root,
        kg_csv_root=kg_csv_root,
        output_dir=output_dir,
        level=args.level
    )


if __name__ == '__main__':
    main()

