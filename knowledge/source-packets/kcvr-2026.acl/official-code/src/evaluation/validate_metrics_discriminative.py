"""
验证评测指标的区分能力
========================

本脚本对比：
1. GT摘要（标准答案，应该得分高）
2. summary_micro_asr（仅从文本生成的摘要，应该得分较低）

如果指标能正确区分两者（GT明显高于ASR-only），说明指标真正有效。

使用示例：
    python src/evaluation/validate_metrics_discriminative.py \
        --std-labels-root data/annotations/standard_labels/micro \
        --raw-labels-root data/annotations/raw_labels/segments \
        --plans-root cache/plans/micro_plans \
        --kg-csv-root knowledge_graph/raw_csv \
        --subjects biology chemistry math physics \
        --output-dir experiments/v7.4_run1/metrics_validation

版本：v1.0
更新：2025-12-30
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List
from collections import defaultdict
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.utils.metric_utils import (
    compute_all_metrics,
    CtlResources,
    KgEdges,
    clean_text_for_eval,
)
from src.evaluation.eval_main import (
    load_ctl_resources,
    load_kg_edges,
    load_plan,
    extract_objectives_and_summary,
)


def load_standard_label(std_labels_root: Path, subject: str, video_id: str, stage: str) -> Dict:
    """加载standard label"""
    video_prefix = video_id.split('_')[1] if '_' in video_id else video_id
    label_file = std_labels_root / subject / video_prefix / f"{video_id}_{stage}.json"
    
    if not label_file.exists():
        return None
    
    with open(label_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_raw_label(raw_labels_root: Path, subject: str, video_id: str, stage: str) -> Dict:
    """加载raw label（包含summary_micro_asr）"""
    # raw_labels路径：segments/{subject}/{video_id_prefix}/{video_id}_{stage}.json
    video_prefix = video_id.split('_')[1] if '_' in video_id else video_id
    label_file = raw_labels_root / subject / video_prefix / f"{video_id}_{stage}.json"
    
    if not label_file.exists():
        return None
    
    with open(label_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def compute_metrics_for_text(text: str,
                             objectives: str,
                             gt_summary: str,
                             gt_objectives: str,
                             plan: Dict,
                             kg_edges: KgEdges,
                             subject: str,
                             ctl_resources: CtlResources) -> Dict[str, float]:
    """
    为单个文本计算所有指标
    
    Args:
        text: 待评测的摘要文本（可能是GT或ASR-only）
        objectives: 对应的学习目标（如果有）
        gt_summary: GT摘要（作为参考）
        gt_objectives: GT学习目标（作为参考）
        plan: plan数据
        kg_edges: KG全局edges
        subject: 学科名
        ctl_resources: CTL资源
        
    Returns:
        metrics dict
    """
    # 提取objectives和summary（如果text包含###格式）
    if "### 学习目标" in text and "### 结构化摘要" in text:
        pred_objectives, pred_summary = extract_objectives_and_summary(
            {"output": text}
        )
    else:
        # 纯文本摘要，没有objectives
        pred_objectives = objectives if objectives else ""
        pred_summary = text
    
    # 计算所有指标
    metrics = compute_all_metrics(
        pred_text=pred_summary,
        ref_text=gt_summary,
        pred_objectives=pred_objectives,
        gold_objectives=gt_objectives,
        plan_pi_kc=plan.get('pi_kc', []),
        plan_edges_based_on=plan.get('edges_based_on', []),
        plan_edges_next=plan.get('edges_next', []),
        subject=subject,
        ctl_resources=ctl_resources,
    )
    
    return metrics


def main():
    parser = argparse.ArgumentParser(description="验证评测指标的区分能力")
    parser.add_argument('--std-labels-root', type=str, required=True,
                       help='标准标注根目录')
    parser.add_argument('--raw-labels-root', type=str, required=True,
                       help='原始标注根目录（包含summary_micro_asr）')
    parser.add_argument('--plans-root', type=str, required=True,
                       help='Plans根目录')
    parser.add_argument('--kg-csv-root', type=str, required=True,
                       help='KG CSV根目录')
    parser.add_argument('--subjects', type=str, nargs='+',
                       default=['biology', 'chemistry', 'math', 'physics'],
                       help='要评测的学科列表')
    parser.add_argument('--output-dir', type=str, required=True,
                       help='输出目录')
    parser.add_argument('--max-samples', type=int, default=50,
                       help='每个学科最多评测的样本数（0=全部）')
    
    args = parser.parse_args()
    
    std_labels_root = Path(args.std_labels_root)
    raw_labels_root = Path(args.raw_labels_root)
    plans_root = Path(args.plans_root)
    kg_csv_root = Path(args.kg_csv_root)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("="*60)
    print("KCVR 评测指标区分能力验证")
    print("="*60)
    print(f"对比：GT摘要 vs summary_micro_asr（ASR-only baseline）")
    print(f"学科：{', '.join(args.subjects)}")
    print()
    
    # 1. 加载资源
    print("[1/4] Loading resources...")
    ctl_resources = load_ctl_resources(kg_csv_root)
    kg_edges = load_kg_edges(kg_csv_root)
    print(f"  Loaded {len(ctl_resources.kc_dict)} KCs")
    print(f"  Loaded {len(kg_edges.based_on)} BASED_ON edges, {len(kg_edges.next)} NEXT edges")
    
    # 2. 收集所有样本
    print("\n[2/4] Collecting samples...")
    samples = []
    
    for subject in args.subjects:
        # 遍历该学科的所有standard labels
        subject_dir = std_labels_root / subject
        if not subject_dir.exists():
            print(f"  Warning: {subject_dir} not found, skipping")
            continue
        
        count = 0
        for video_dir in subject_dir.iterdir():
            if not video_dir.is_dir():
                continue
            
            for label_file in video_dir.glob("*.json"):
                if count >= args.max_samples > 0:
                    break
                
                # 解析文件名：{video_id}_{stage}.json
                name = label_file.stem
                if '_' not in name:
                    continue
                
                parts = name.rsplit('_', 1)
                if len(parts) != 2:
                    continue
                
                video_id = f"{subject}_{parts[0].split('_')[-1]}"
                stage = parts[1]
                
                # 加载standard label
                std_label = load_standard_label(std_labels_root, subject, video_id, stage)
                if not std_label:
                    continue
                
                # 加载raw label
                raw_label = load_raw_label(raw_labels_root, subject, video_id, stage)
                if not raw_label or 'summary_micro_asr' not in raw_label:
                    continue
                
                # 加载plan
                plan = load_plan(plans_root, {
                    'subject': subject,
                    'video_id': video_id,
                    'segment_id': std_label.get('segment_id', ''),
                })
                
                samples.append({
                    'subject': subject,
                    'video_id': video_id,
                    'stage': stage,
                    'std_label': std_label,
                    'raw_label': raw_label,
                    'plan': plan,
                })
                
                count += 1
        
        print(f"  {subject}: {count} samples")
    
    print(f"\n  Total: {len(samples)} samples")
    
    # 3. 计算指标
    print("\n[3/4] Computing metrics...")
    results = []
    
    for i, sample in enumerate(samples):
        if (i + 1) % 20 == 0:
            print(f"  Progress: {i+1}/{len(samples)}")
        
        subject = sample['subject']
        std_label = sample['std_label']
        raw_label = sample['raw_label']
        plan = sample['plan']
        
        # GT摘要和目标
        gt_summary = std_label.get('summary_gt', '') or std_label.get('summary_target', '')
        gt_objectives = std_label.get('objectives_gt', '') or std_label.get('learning_objectives', '')
        if isinstance(gt_objectives, list):
            gt_objectives = '\n'.join(gt_objectives)
        
        # ASR-only摘要
        asr_summary = raw_label.get('summary_micro_asr', '')
        
        if not gt_summary or not asr_summary:
            continue
        
        try:
            # 计算GT的指标（作为上界）
            gt_metrics = compute_metrics_for_text(
                text=gt_summary,
                objectives=gt_objectives,
                gt_summary=gt_summary,
                gt_objectives=gt_objectives,
                plan=plan,
                kg_edges=kg_edges,
                subject=subject,
                ctl_resources=ctl_resources,
            )
            
            # 计算ASR-only的指标（作为baseline）
            asr_metrics = compute_metrics_for_text(
                text=asr_summary,
                objectives="",  # ASR-only没有objectives
                gt_summary=gt_summary,
                gt_objectives=gt_objectives,
                plan=plan,
                kg_edges=kg_edges,
                subject=subject,
                ctl_resources=ctl_resources,
            )
            
            results.append({
                'subject': subject,
                'video_id': sample['video_id'],
                'stage': sample['stage'],
                **{f'GT_{k}': v for k, v in gt_metrics.items()},
                **{f'ASR_{k}': v for k, v in asr_metrics.items()},
                **{f'Gap_{k}': gt_metrics[k] - asr_metrics[k] for k in gt_metrics.keys()},
            })
            
        except Exception as e:
            print(f"  Warning: Failed for {subject}/{sample['video_id']}/{sample['stage']}: {e}")
            continue
    
    print(f"  Successfully computed metrics for {len(results)}/{len(samples)} samples")
    
    # 4. 统计分析
    print("\n[4/4] Computing statistics...")
    
    df = pd.DataFrame(results)
    
    # 按学科统计
    by_subject = {}
    for subject in args.subjects:
        subject_df = df[df['subject'] == subject]
        if len(subject_df) == 0:
            continue
        
        by_subject[subject] = {
            'n_samples': len(subject_df),
            'GT_mean': {k.replace('GT_', ''): subject_df[f'GT_{k.replace("GT_", "")}'].mean() 
                       for k in subject_df.columns if k.startswith('GT_')},
            'ASR_mean': {k.replace('ASR_', ''): subject_df[f'ASR_{k.replace("ASR_", "")}'].mean() 
                        for k in subject_df.columns if k.startswith('ASR_')},
            'Gap_mean': {k.replace('Gap_', ''): subject_df[f'Gap_{k.replace("Gap_", "")}'].mean() 
                         for k in subject_df.columns if k.startswith('Gap_')},
        }
    
    # 全局平均
    global_stats = {
        'n_samples': len(df),
        'GT_mean': {k.replace('GT_', ''): df[k].mean() for k in df.columns if k.startswith('GT_')},
        'ASR_mean': {k.replace('ASR_', ''): df[k].mean() for k in df.columns if k.startswith('ASR_')},
        'Gap_mean': {k.replace('Gap_', ''): df[k].mean() for k in df.columns if k.startswith('Gap_')},
    }
    
    # 5. 输出结果
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    
    # 打印全局平均
    print("\n【Global Average】")
    print(f"  Samples: {global_stats['n_samples']}")
    print(f"\n  {'Metric':<10} {'GT (Upper)':<12} {'ASR (Baseline)':<15} {'Gap':<10} {'Status'}")
    print("  " + "-"*60)
    
    key_metrics = ['R1', 'R2', 'RL', 'BS', 'C-F1', 'KPC', 'LOC']
    for metric in key_metrics:
        gt_val = global_stats['GT_mean'].get(metric, 0)
        asr_val = global_stats['ASR_mean'].get(metric, 0)
        gap = global_stats['Gap_mean'].get(metric, 0)
        
        # 判断指标是否有效：GT应该明显高于ASR
        status = "✅" if gap > 0.05 else "⚠️" if gap > 0 else "❌"
        
        print(f"  {metric:<10} {gt_val:<12.4f} {asr_val:<15.4f} {gap:<10.4f} {status}")
    
    # 打印按学科统计
    print("\n【Per-Subject Average】")
    for subject, stats in by_subject.items():
        print(f"\n  {subject.upper()} (n={stats['n_samples']})")
        print(f"    {'Metric':<10} {'GT':<12} {'ASR':<15} {'Gap':<10}")
        print("    " + "-"*50)
        for metric in key_metrics:
            gt_val = stats['GT_mean'].get(metric, 0)
            asr_val = stats['ASR_mean'].get(metric, 0)
            gap = stats['Gap_mean'].get(metric, 0)
            print(f"    {metric:<10} {gt_val:<12.4f} {asr_val:<15.4f} {gap:<10.4f}")
    
    # 保存详细结果
    output_csv = output_dir / "metrics_comparison.csv"
    df.to_csv(output_csv, index=False, float_format='%.4f')
    print(f"\n✅ Detailed results saved to: {output_csv}")
    
    # 保存统计摘要
    output_json = output_dir / "metrics_comparison_summary.json"
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump({
            'global': global_stats,
            'by_subject': by_subject,
        }, f, indent=2, ensure_ascii=False)
    print(f"✅ Summary saved to: {output_json}")
    
    # 判断指标是否有效
    print("\n" + "="*60)
    print("VALIDATION CONCLUSION")
    print("="*60)
    
    all_valid = True
    for metric in key_metrics:
        gap = global_stats['Gap_mean'].get(metric, 0)
        if gap <= 0:
            print(f"❌ {metric}: Gap={gap:.4f} (GT <= ASR, indicator may not be discriminative)")
            all_valid = False
        elif gap < 0.05:
            print(f"⚠️  {metric}: Gap={gap:.4f} (GT > ASR but gap is small)")
        else:
            print(f"✅ {metric}: Gap={gap:.4f} (GT significantly better than ASR)")
    
    if all_valid:
        print("\n🎉 All indicators are discriminative! Ready for fine-tuning.")
    else:
        print("\n⚠️  Some indicators may need adjustment before fine-tuning.")
    
    print("="*60)


if __name__ == '__main__':
    main()

