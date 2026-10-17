"""
KCVR GT vs ASR-only 对比验证
================================

功能：
1. 加载 GT summary 和 ASR-only summary
2. 对两者分别计算所有指标（ROUGE, BERTScore, C-F1, KPC, LOC）
3. 对比验证：GT 的教育指标（KPC/LOC/C-F1）应优于 ASR-only
4. 生成详细的对比报告

使用示例：
    python src/evaluation/validate_gt_vs_asr.py \\
        --labels-root data/annotations/standard_labels/micro \\
        --plans-root cache/plans/micro_plans \\
        --kg-csv-root knowledge_graph/raw_csv \\
        --alias-root knowledge_graph/alias \\
        --subjects biology chemistry \\
        --max-samples 50 \\
        --output-dir experiments/v7.4_run1/gt_vs_asr_validation

版本：v1.0
更新：2025-12-31
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
import csv

# 添加项目根目录到 sys.path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.utils.metric_utils import (
    compute_all_metrics,
    CtlResources,
    clean_text_for_eval
)


def load_label(label_file: Path) -> Dict:
    """加载标注文件"""
    with open(label_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_plan(plan_file: Path) -> Dict:
    """加载 plan 文件"""
    if not plan_file.exists():
        return {}
    with open(plan_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_summaries(label: Dict, raw_label: Dict = None) -> Tuple[str, str, str]:
    """
    提取 GT summary, ASR-only summary, objectives
    
    Args:
        label: standard_labels 中的标注
        raw_label: raw_labels 中的标注（包含 ASR summary）
    
    Returns:
        (summary_gt, summary_asr, objectives_gt)
    """
    # GT summary (cleaned)
    summary_gt = label.get('summary_plain', '') or label.get('summary_gt', '')
    if not summary_gt:
        # Fallback: 从原始 summary_gt 中提取（去除 markdown）
        raw_summary = label.get('summary_gt', '')
        summary_gt = clean_text_for_eval(raw_summary)
    
    # ASR-only summary (from raw labels)
    summary_asr = ''
    if raw_label:
        summary_asr = raw_label.get('summary_micro_asr', '')
    if not summary_asr:
        # Fallback: 从 standard_labels 中尝试加载
        summary_asr = label.get('summary_micro_asr', '')
    summary_asr = clean_text_for_eval(summary_asr) if summary_asr else ''
    
    # Objectives
    objectives_gt = label.get('objectives_plain', '') or label.get('objectives_gt', '')
    if not objectives_gt:
        objectives_list = label.get('learning_objectives', [])
        if isinstance(objectives_list, list):
            objectives_gt = '\n'.join(str(obj) for obj in objectives_list)
        else:
            objectives_gt = str(objectives_list)
    
    # 确保 objectives_gt 是字符串
    if isinstance(objectives_gt, list):
        objectives_gt = '\n'.join(str(obj) for obj in objectives_gt)
    
    objectives_gt = clean_text_for_eval(str(objectives_gt))
    
    return summary_gt, summary_asr, objectives_gt


def main():
    parser = argparse.ArgumentParser(description="KCVR GT vs ASR-only 验证")
    parser.add_argument('--labels-root', type=str, required=True,
                       help='标注根目录（data/annotations/standard_labels/micro）')
    parser.add_argument('--raw-labels-root', type=str, required=True,
                       help='原始标注根目录（data/annotations/raw_labels/segments）')
    parser.add_argument('--plans-root', type=str, required=True,
                       help='Plans 根目录（cache/plans/micro_plans）')
    parser.add_argument('--kg-csv-root', type=str, required=True,
                       help='KG CSV 根目录（knowledge_graph/raw_csv）')
    parser.add_argument('--alias-root', type=str, required=True,
                       help='Alias 表根目录（knowledge_graph/alias）')
    parser.add_argument('--subjects', type=str, nargs='+', required=True,
                       help='指定学科列表（如 biology chemistry）')
    parser.add_argument('--max-samples', type=int, default=50,
                       help='每个学科的最大样本数（默认 50）')
    parser.add_argument('--output-dir', type=str, required=True,
                       help='输出目录')
    
    args = parser.parse_args()
    
    labels_root = Path(args.labels_root)
    raw_labels_root = Path(args.raw_labels_root)
    plans_root = Path(args.plans_root)
    kg_csv_root = Path(args.kg_csv_root)
    alias_root = Path(args.alias_root)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("="*60)
    print("KCVR GT vs ASR-only 对比验证")
    print("="*60)
    print(f"Labels root: {labels_root}")
    print(f"Plans root: {plans_root}")
    print(f"Subjects: {args.subjects}")
    print(f"Max samples per subject: {args.max_samples}")
    print()
    
    # 加载 CTL resources（全局共享）
    print("[1/4] Loading CTL resources...")
    
    # 加载 KC 字典
    kc_dict = {}
    kc_csv = kg_csv_root / "nodes_kc.csv"
    if kc_csv.exists():
        import csv as csv_module
        with open(kc_csv, 'r', encoding='utf-8') as f:
            reader = csv_module.DictReader(f)
            for row in reader:
                kc_id = row.get('id', '')
                name = row.get('name', '')
                if kc_id and name:
                    kc_dict[kc_id] = name
    
    # 加载 alias 表（作为 synonyms）
    kc_synonyms = {}
    for subject in args.subjects:
        alias_file = alias_root / f"{subject}_alias.json"
        if alias_file.exists():
            with open(alias_file, 'r', encoding='utf-8') as f:
                alias_data = json.load(f)
                for kc_id, info in alias_data.items():
                    if kc_id not in kc_synonyms:
                        kc_synonyms[kc_id] = []
                    aliases = info.get('aliases', [])
                    kc_synonyms[kc_id].extend(aliases)
    
    # 创建 CtlResources (dataclass)
    ctl_resources = CtlResources(
        kc_dict=kc_dict,
        kc_synonyms=kc_synonyms,
        trie=None,
        normalizer=None
    )
    
    print(f"  ✅ Loaded {len(kc_dict)} KC nodes, {len(kc_synonyms)} with aliases")
    
    # 结果存储
    all_results = []
    stats_by_subject = defaultdict(lambda: {'gt': [], 'asr': []})
    
    # 逐学科处理
    for subject in args.subjects:
        print(f"\n[{subject}]")
        subject_labels_root = labels_root / subject
        subject_plans_root = plans_root / subject
        
        if not subject_labels_root.exists():
            print(f"  ⚠️  Labels directory not found: {subject_labels_root}")
            continue
        
        # 遍历所有视频目录
        sample_count = 0
        for video_dir in sorted(subject_labels_root.iterdir()):
            if not video_dir.is_dir():
                continue
            
            video_id_prefix = video_dir.name  # e.g., "001"
            
            # 遍历该视频的所有标注文件
            for label_file in sorted(video_dir.glob("*.json")):
                if sample_count >= args.max_samples:
                    break
                
                # 解析文件名：{subject}_{video_id}_{stage}.json
                label_name = label_file.stem
                parts = label_name.split('_')
                if len(parts) < 3:
                    continue
                
                video_id = f"{parts[0]}_{parts[1]}"  # e.g., "biology_001"
                stage = parts[2]  # e.g., "intro"
                
                # 映射 stage 到 segment_id
                stage_map = {
                    'intro': 'seg_0001',
                    'exposition': 'seg_0002',
                    'interaction': 'seg_0003',
                    'conclusion': 'seg_0004',
                }
                segment_id = stage_map.get(stage, '')
                if not segment_id:
                    continue
                
                # 加载 label
                try:
                    label = load_label(label_file)
                except Exception as e:
                    print(f"  ⚠️  Failed to load {label_file.name}: {e}")
                    continue
                
                # 加载 raw label (for ASR summary)
                raw_label_file = raw_labels_root / subject / video_id_prefix / label_file.name
                raw_label = None
                if raw_label_file.exists():
                    try:
                        raw_label = load_label(raw_label_file)
                    except Exception as e:
                        print(f"  ⚠️  Failed to load raw label {raw_label_file.name}: {e}")
                
                # 提取 summaries
                summary_gt, summary_asr, objectives_gt = extract_summaries(label, raw_label)
                
                if not summary_gt or not objectives_gt:
                    print(f"  ⚠️  Missing GT data in {label_file.name}")
                    continue
                
                if not summary_asr:
                    print(f"  ⚠️  Missing ASR summary in {label_file.name}, skipping")
                    continue
                
                # 加载 plan
                # NOTE: plans 的真实目录结构是：
                #   cache/plans/micro_plans/{subject}/{video_id}/{video_id}__{seg_id}.json
                # 例如：
                #   cache/plans/micro_plans/biology/biology_001/biology_001__seg_0001.json
                plan_file = subject_plans_root / video_id / f"{video_id}__{segment_id}.json"
                plan = load_plan(plan_file)
                
                if not plan:
                    print(f"  ⚠️  Missing plan for {video_id}__{segment_id} (expected: {plan_file})")
                    continue
                
                # 计算指标：GT
                try:
                    metrics_gt = compute_all_metrics(
                        pred_text=summary_gt,
                        ref_text=summary_gt,  # GT 作为 reference
                        pred_objectives='',  # 不需要
                        gold_objectives=objectives_gt,
                        subject=subject,
                        ctl_resources=ctl_resources,
                        plan_pi_kc=plan.get('pi_kc', []) or plan.get('pi', []),
                        plan_edges_based_on=plan.get('edges_based_on', []),
                        plan_edges_next=plan.get('edges_next', []),
                    )
                except Exception as e:
                    print(f"  ⚠️  Failed to compute GT metrics for {label_file.name}: {e}")
                    continue
                
                # 计算指标：ASR-only
                try:
                    metrics_asr = compute_all_metrics(
                        pred_text=summary_asr,
                        ref_text=summary_gt,  # 仍以 GT 作为 reference
                        pred_objectives='',  # ASR-only 没有显式 objectives
                        gold_objectives=objectives_gt,
                        subject=subject,
                        ctl_resources=ctl_resources,
                        plan_pi_kc=plan.get('pi_kc', []) or plan.get('pi', []),
                        plan_edges_based_on=plan.get('edges_based_on', []),
                        plan_edges_next=plan.get('edges_next', []),
                    )
                except Exception as e:
                    print(f"  ⚠️  Failed to compute ASR metrics for {label_file.name}: {e}")
                    continue
                
                # 记录结果
                result = {
                    'subject': subject,
                    'video_id': video_id,
                    'segment_id': segment_id,
                    'stage': stage,
                    # GT metrics
                    'gt_r1': metrics_gt.get('R1', 0.0),
                    'gt_r2': metrics_gt.get('R2', 0.0),
                    'gt_rl': metrics_gt.get('RL', 0.0),
                    'gt_bs': metrics_gt.get('BS', 0.0),
                    'gt_cf1': metrics_gt.get('C-F1', 0.0),
                    'gt_kpc': metrics_gt.get('KPC', 0.0),
                    'gt_loc': metrics_gt.get('LOC', 0.0),
                    # ASR metrics
                    'asr_r1': metrics_asr.get('R1', 0.0),
                    'asr_r2': metrics_asr.get('R2', 0.0),
                    'asr_rl': metrics_asr.get('RL', 0.0),
                    'asr_bs': metrics_asr.get('BS', 0.0),
                    'asr_cf1': metrics_asr.get('C-F1', 0.0),
                    'asr_kpc': metrics_asr.get('KPC', 0.0),
                    'asr_loc': metrics_asr.get('LOC', 0.0),
                }
                
                all_results.append(result)
                stats_by_subject[subject]['gt'].append(metrics_gt)
                stats_by_subject[subject]['asr'].append(metrics_asr)
                
                sample_count += 1
        
        print(f"  ✅ Processed {sample_count} samples")
    
    # 写入详细结果 CSV
    print(f"\n[3/4] Writing detailed results...")
    csv_file = output_dir / "gt_vs_asr_detailed.csv"
    fieldnames = [
        'subject', 'video_id', 'segment_id', 'stage',
        'gt_r1', 'gt_r2', 'gt_rl', 'gt_bs', 'gt_cf1', 'gt_kpc', 'gt_loc',
        'asr_r1', 'asr_r2', 'asr_rl', 'asr_bs', 'asr_cf1', 'asr_kpc', 'asr_loc',
    ]
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for result in all_results:
            writer.writerow(result)
    print(f"  ✅ Saved to: {csv_file}")
    
    # 计算统计和对比
    print(f"\n[4/4] Computing statistics...")
    
    summary_report = []
    summary_report.append("="*80)
    summary_report.append("GT vs ASR-only 验证报告")
    summary_report.append("="*80)
    summary_report.append("")
    
    for subject in args.subjects:
        if subject not in stats_by_subject:
            continue
        
        gt_metrics = stats_by_subject[subject]['gt']
        asr_metrics = stats_by_subject[subject]['asr']
        
        if not gt_metrics or not asr_metrics:
            continue
        
        n = len(gt_metrics)
        summary_report.append(f"\n[{subject.upper()}] (n={n})")
        summary_report.append("-"*80)
        
        # 计算平均值
        metric_names = ['R1', 'R2', 'RL', 'BS', 'C-F1', 'KPC', 'LOC']
        
        summary_report.append(f"{'Metric':<10} {'GT Mean':<12} {'ASR Mean':<12} {'Δ (GT-ASR)':<15} {'Conclusion'}")
        summary_report.append("-"*80)
        
        for metric in metric_names:
            gt_values = [m.get(metric, 0.0) for m in gt_metrics]
            asr_values = [m.get(metric, 0.0) for m in asr_metrics]
            
            gt_mean = sum(gt_values) / len(gt_values) if gt_values else 0.0
            asr_mean = sum(asr_values) / len(asr_values) if asr_values else 0.0
            delta = gt_mean - asr_mean
            
            # 判断是否符合预期
            if metric in ['KPC', 'LOC', 'C-F1']:
                # 教育指标：GT 应该更高
                if delta > 0.05:
                    conclusion = "✅ GT > ASR"
                elif delta > 0:
                    conclusion = "⚠️  GT ≈ ASR (small gap)"
                else:
                    conclusion = "❌ GT < ASR (unexpected!)"
            else:
                # 生成类指标：GT 应该接近 1.0
                if gt_mean > 0.8:
                    conclusion = "✅ GT high"
                elif gt_mean > 0.6:
                    conclusion = "⚠️  GT moderate"
                else:
                    conclusion = "❌ GT low"
            
            summary_report.append(
                f"{metric:<10} {gt_mean:<12.4f} {asr_mean:<12.4f} {delta:+<15.4f} {conclusion}"
            )
    
    summary_report.append("\n" + "="*80)
    summary_report.append("验证标准:")
    summary_report.append("="*80)
    summary_report.append("✅ 符合预期: GT 的教育指标 (KPC/LOC/C-F1) 明显高于 ASR-only (Δ > 0.05)")
    summary_report.append("⚠️  需注意: Δ 较小 (0 < Δ ≤ 0.05)，可能需要调整指标实现")
    summary_report.append("❌ 不符合预期: GT ≤ ASR-only，指标实现可能有问题")
    summary_report.append("")
    summary_report.append("说明:")
    summary_report.append("- R1/R2/RL/BS: GT 对 GT 应接近 1.0（完美匹配）")
    summary_report.append("- KPC/LOC/C-F1: GT 应明显优于 ASR-only（体现结构化指导的价值）")
    summary_report.append("="*80)
    
    # 输出到终端和文件
    summary_text = '\n'.join(summary_report)
    print('\n' + summary_text)
    
    summary_file = output_dir / "gt_vs_asr_summary.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary_text)
    print(f"\n✅ Summary saved to: {summary_file}")
    
    print("\n" + "="*80)
    print("✅ Validation completed!")
    print("="*80)


if __name__ == '__main__':
    main()

