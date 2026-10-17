# KCVR evaluation main entry
# Computes all metrics (ROUGE, BERTScore, C-F1, KPC, LOC) and outputs results

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
import pandas as pd

# 添加项目根目录到 sys.path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.utils.metric_utils import (
    compute_all_metrics,
    CtlResources,
    KgEdges,
)


def load_ctl_resources(kg_csv_root: Path, subject: str = None) -> CtlResources:
    """
    加载 CTL 所需资源（KC 字典、同义词等）
    
    Args:
        kg_csv_root: KG CSV 文件根目录
        subject: 学科名（可选，用于过滤）
        
    Returns:
        CtlResources
    """
    kc_dict = {}
    kc_synonyms = {}
    
    # 读取 nodes_kc.csv
    kc_csv = kg_csv_root / "nodes_kc.csv"
    if kc_csv.exists():
        import csv
        with open(kc_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                kc_id = row['id']
                kc_name = row['name']
                kc_dict[kc_id] = kc_name
                
                # Load synonyms if available
                # kc_synonyms[kc_id] = ...
    
    return CtlResources(
        kc_dict=kc_dict,
        kc_synonyms=kc_synonyms,
        trie=None,  # Optional: can be optimized with trie structure
        normalizer=None,
    )


def load_kg_edges(kg_csv_root: Path, subject: str = None) -> KgEdges:
    """
    加载知识图谱边（BASED_ON + NEXT）
    
    Args:
        kg_csv_root: KG CSV 文件根目录
        subject: 学科名（可选，用于过滤）
        
    Returns:
        KgEdges
    """
    based_on_edges = []
    next_edges = []
    
    # 读取 relations.csv
    relations_csv = kg_csv_root / "relations.csv"
    if relations_csv.exists():
        import csv
        with open(relations_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 列名可能是 'relation' 或 ':TYPE'
                rel_type = row.get('relation') or row.get(':TYPE') or row.get('type')
                start = row.get('start') or row.get(':START_ID') or row.get('start_id')
                end = row.get('end') or row.get(':END_ID') or row.get('end_id')
                
                if rel_type == 'BASED_ON':
                    based_on_edges.append((start, end))
                elif rel_type == 'NEXT':
                    next_edges.append((start, end))
    
    return KgEdges(
        based_on=based_on_edges,
        next=next_edges,
    )


def load_predictions(pred_jsonl: Path) -> List[Dict]:
    """加载预测文件"""
    predictions = []
    with open(pred_jsonl, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                predictions.append(json.loads(line))
    return predictions


def load_ground_truth(labels_root: Path, meta: Dict) -> Dict:
    """
    加载 ground truth（objectives + summary + knowledge_points）
    
    Args:
        labels_root: standard_labels 根目录
        meta: 包含 subject/video_id/segment_id/stage 的元数据
        
    Returns:
        {"objectives": str, "summary": str, "knowledge_points": List[str]}
    """
    subject = meta['subject']
    video_id = meta['video_id']
    stage = meta.get('stage', '')
    
    # 实际文件命名是：{video_id}_{stage}.json (如 biology_001_intro.json)
    video_prefix = video_id.split('_')[1] if '_' in video_id else video_id
    label_file = labels_root / subject / video_prefix / f"{video_id}_{stage}.json"
    
    if not label_file.exists():
        print(f"Warning: Label file not found: {label_file}")
        return {"objectives": "", "summary": "", "knowledge_points": []}
    
    with open(label_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # objectives 可能是 list 或 str，统一转为 str
    objectives = data.get('objectives_gt') or data.get('learning_objectives', '')
    if isinstance(objectives, list):
        objectives = '\n'.join(objectives)
    
    return {
        "objectives": objectives,
        "summary": data.get('summary_gt', '') or data.get('summary_target', ''),
        "knowledge_points": data.get('knowledge_points', []),
    }


def load_plan(plans_root: Path, meta: Dict) -> Dict:
    """
    加载 Plan（π + edges）
    
    Args:
        plans_root: plans 根目录
        meta: 包含 subject/video_id/segment_id 的元数据
        
    Returns:
        {"pi_kc": List[str], "edges_based_on": ..., "edges_next": ...}
    """
    subject = meta['subject']
    video_id = meta['video_id']
    segment_id = meta['segment_id']
    
    # 构造路径：cache/plans/micro_plans/{subject}/{video_id}/{video_id}__{segment_id}.json
    plan_file = plans_root / subject / video_id / f"{video_id}__{segment_id}.json"
    
    if not plan_file.exists():
        print(f"Warning: Plan file not found: {plan_file}")
        return {"pi_kc": [], "edges_based_on": [], "edges_next": []}
    
    with open(plan_file, 'r', encoding='utf-8') as f:
        plan = json.load(f)
    
    # 提取 π（教学递进路径）
    pi_kc = plan.get('pi_kc', [])
    
    # 提取 edges（从 plan 的 subgraph 中）
    edges_based_on = []
    edges_next = []
    
    for edge in plan.get('edges_based_on', []):
        if isinstance(edge, dict):
            edges_based_on.append((edge['from'], edge['to']))
        elif isinstance(edge, (list, tuple)) and len(edge) == 2:
            edges_based_on.append(tuple(edge))
    
    for edge in plan.get('edges_next', []):
        if isinstance(edge, dict):
            edges_next.append((edge['from'], edge['to']))
        elif isinstance(edge, (list, tuple)) and len(edge) == 2:
            edges_next.append(tuple(edge))
    
    return {
        "pi_kc": pi_kc,
        "edges_based_on": edges_based_on,
        "edges_next": edges_next,
    }


def extract_objectives_and_summary(pred_output: str) -> Tuple[str, str]:
    """
    从模型输出中提取学习目标和结构化摘要
    
    期望格式：
        ### 学习目标
        ...
        ### 结构化摘要
        ...
        
    注意：摘要部分可能包含子标题（如 ### 【导入·认知锚定】），需要全部保留
        
    Returns:
        (objectives, summary)
    """
    import re
    
    # 方案：按 ### 学习目标 和 ### 结构化摘要 分段
    parts = re.split(r'###\s*(学习目标|结构化摘要)\s*\n', pred_output)
    
    objectives = ""
    summary = ""
    
    for i in range(1, len(parts), 2):  # parts[1], parts[3], ... 是标题
        if i + 1 < len(parts):
            section_title = parts[i]
            section_content = parts[i + 1].strip()
            
            if '学习目标' in section_title:
                objectives = section_content
            elif '结构化摘要' in section_title:
                # 摘要部分：保留所有内容（包括子标题）
                summary = section_content
    
    # Fallback：如果都提取失败，整个output作为summary
    if not objectives and not summary:
        summary = pred_output.strip()
    
    return objectives, summary


def compute_metrics_for_sample(pred: Dict,
                               gt: Dict,
                               plan: Dict,
                               kg_edges: KgEdges,
                               ctl_resources: CtlResources) -> Dict[str, float]:
    """
    为单个样本计算所有指标
    
    Args:
        pred: 预测数据（含 meta + output）
        gt: ground truth
        plan: plan 数据（包含 pi_kc, edges_based_on, edges_next）
        kg_edges: KG 全局边（用于其他指标，KPC 不再使用）
        ctl_resources: CTL 资源
        
    Returns:
        metrics dict
        
    关键修正（2025-12-31）：
        - KPC 计算使用 plan 的边集合，而不是全局 KG 的所有边
        - 理由：论文定义 KPC 的分母是"该视频/课程的依赖边集合"，不是整张学科 KG
        - 这样避免大量无关边被计入，导致 KPC 系统性偏低
    """
    # 提取预测的目标和摘要
    pred_objectives, pred_summary = extract_objectives_and_summary(pred['output'])
    
    # 计算所有指标（KPC 使用 plan 的边集合）
    metrics = compute_all_metrics(
        pred_text=pred_summary,
        ref_text=gt['summary'],
        pred_objectives=pred_objectives,
        gold_objectives=gt['objectives'],
        plan_pi_kc=plan.get('pi_kc', []),
        plan_edges_based_on=plan.get('edges_based_on', []),
        plan_edges_next=plan.get('edges_next', []),
        subject=pred['meta']['subject'],
        ctl_resources=ctl_resources,
    )
    
    return metrics


def macro_average_across_subjects(results: List[Dict]) -> Dict[str, float]:
    """
    按学科先平均，再跨学科平均（Macro-average across subjects）
    
    这是论文表格要求的统计口径，避免样本多的学科拉高均值
    
    Args:
        results: List of {meta, metrics}
        
    Returns:
        macro-averaged metrics
    """
    # 按学科分组
    by_subject = defaultdict(list)
    for r in results:
        subject = r['meta']['subject']
        by_subject[subject].append(r['metrics'])
    
    # 每个学科内先平均
    subject_means = {}
    for subject, metrics_list in by_subject.items():
        subject_mean = {}
        for key in metrics_list[0].keys():
            values = [m[key] for m in metrics_list if key in m]
            subject_mean[key] = sum(values) / max(1, len(values))
        subject_means[subject] = subject_mean
    
    # 跨学科平均
    macro_avg = {}
    all_keys = set()
    for sm in subject_means.values():
        all_keys.update(sm.keys())
    
    for key in all_keys:
        values = [sm[key] for sm in subject_means.values() if key in sm]
        macro_avg[key] = sum(values) / max(1, len(values))
    
    return macro_avg


def main():
    parser = argparse.ArgumentParser(description="KCVR 统一评测主入口")
    parser.add_argument('--predictions', type=str, required=True,
                       help='预测文件路径 (predictions.jsonl)')
    parser.add_argument('--labels-root', type=str, required=True,
                       help='标注根目录 (data/annotations/standard_labels/micro)')
    parser.add_argument('--plans-root', type=str, required=True,
                       help='Plans 根目录 (cache/plans/micro_plans)')
    parser.add_argument('--kg-csv-root', type=str, required=True,
                       help='KG CSV 根目录 (knowledge_graph/raw_csv)')
    parser.add_argument('--splits', type=str, default=None,
                       help='Split 文件 (可选，用于过滤 in-domain/OOD)')
    parser.add_argument('--split', type=str, default='test',
                       choices=['train', 'val', 'test', 'ood'],
                       help='评测哪个 split')
    parser.add_argument('--output-dir', type=str, required=True,
                       help='输出目录')
    
    args = parser.parse_args()
    
    # 转换为 Path
    pred_file = Path(args.predictions)
    labels_root = Path(args.labels_root)
    plans_root = Path(args.plans_root)
    kg_csv_root = Path(args.kg_csv_root)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"[KCVR Evaluation] Starting evaluation on split: {args.split}")
    print(f"  Predictions: {pred_file}")
    print(f"  Output dir: {output_dir}")
    
    # 1. 加载资源
    print("\n[1/5] Loading resources...")
    ctl_resources = load_ctl_resources(kg_csv_root)
    kg_edges = load_kg_edges(kg_csv_root)
    print(f"  Loaded {len(ctl_resources.kc_dict)} KCs")
    print(f"  Loaded {len(kg_edges.based_on)} BASED_ON edges, {len(kg_edges.next)} NEXT edges")
    
    # 2. 加载预测
    print("\n[2/5] Loading predictions...")
    predictions = load_predictions(pred_file)
    print(f"  Loaded {len(predictions)} predictions")
    
    # 3. 逐样本计算指标
    print("\n[3/5] Computing metrics for each sample...")
    results = []
    
    for i, pred in enumerate(predictions):
        if (i + 1) % 50 == 0:
            print(f"  Progress: {i+1}/{len(predictions)}")
        
        try:
            # 加载 ground truth
            gt = load_ground_truth(labels_root, pred['meta'])
            
            # 加载 plan
            plan = load_plan(plans_root, pred['meta'])
            
            # 计算指标
            metrics = compute_metrics_for_sample(
                pred=pred,
                gt=gt,
                plan=plan,
                kg_edges=kg_edges,
                ctl_resources=ctl_resources,
            )
            
            results.append({
                'meta': pred['meta'],
                'metrics': metrics,
            })
            
        except Exception as e:
            print(f"  Warning: Failed to compute metrics for sample {i}: {e}")
            continue
    
    print(f"  Successfully computed metrics for {len(results)}/{len(predictions)} samples")
    
    # 4. 统计
    print("\n[4/5] Computing statistics...")
    
    # Per-sample results
    per_sample_df = pd.DataFrame([
        {**r['meta'], **r['metrics']} for r in results
    ])
    
    # Per-subject average
    by_subject = defaultdict(list)
    for r in results:
        by_subject[r['meta']['subject']].append(r['metrics'])
    
    subject_stats = []
    for subject, metrics_list in by_subject.items():
        subject_mean = {}
        subject_mean['subject'] = subject
        subject_mean['split'] = args.split
        subject_mean['n_samples'] = len(metrics_list)
        
        for key in metrics_list[0].keys():
            values = [m[key] for m in metrics_list if key in m]
            subject_mean[key] = sum(values) / max(1, len(values))
        
        subject_stats.append(subject_mean)
    
    subject_df = pd.DataFrame(subject_stats)
    
    # Macro-average across subjects
    macro_avg = macro_average_across_subjects(results)
    macro_avg['subject'] = 'MACRO_AVG'
    macro_avg['split'] = args.split
    macro_avg['n_samples'] = len(results)
    
    # 5. 输出
    print("\n[5/5] Saving results...")
    
    # JSON（完整结果）
    output_json = output_dir / f"metrics_{args.split}.json"
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump({
            'split': args.split,
            'n_samples': len(results),
            'n_subjects': len(by_subject),
            'macro_avg': macro_avg,
            'per_subject': subject_stats,
            'per_sample': [
                {**r['meta'], **r['metrics']} for r in results
            ],
        }, f, indent=2, ensure_ascii=False)
    
    print(f"  Saved JSON: {output_json}")
    
    # CSV（表格友好）
    output_csv = output_dir / f"metrics_{args.split}.csv"
    
    # 合并 per-subject + macro-avg 到一个 CSV
    final_df = pd.concat([
        subject_df,
        pd.DataFrame([macro_avg]),
    ], ignore_index=True)
    
    # 按论文表格列名排序
    column_order = ['subject', 'split', 'n_samples', 'R1', 'R2', 'RL', 'BS', 'C-F1', 'KPC', 'LOC']
    existing_cols = [c for c in column_order if c in final_df.columns]
    other_cols = [c for c in final_df.columns if c not in existing_cols]
    
    final_df = final_df[existing_cols + other_cols]
    final_df.to_csv(output_csv, index=False, float_format='%.4f')
    
    print(f"  Saved CSV: {output_csv}")
    
    # 打印 macro-avg
    print("\n" + "="*60)
    print(f"MACRO-AVERAGE RESULTS ({args.split.upper()})")
    print("="*60)
    for key in ['R1', 'R2', 'RL', 'BS', 'C-F1', 'KPC', 'LOC']:
        if key in macro_avg:
            print(f"  {key:8s}: {macro_avg[key]:.4f}")
    print("="*60)
    
    print("\n✅ Evaluation completed successfully!")


if __name__ == '__main__':
    main()

