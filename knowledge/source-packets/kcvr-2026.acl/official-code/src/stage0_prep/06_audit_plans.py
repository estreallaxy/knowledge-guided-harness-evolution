"""
KCVR Planner 质量审计脚本
=======================

功能：
1. KC 覆盖率：plan 的 KC 覆盖了多少 label 的 kp
2. π 可讲述性：π 中的节点在 transcript 中的出现率
3. TP 完整性：TP 与 HAS_CONCEPT 的完整性

使用示例：
    python src/stage0_prep/06_audit_plans.py \\
        --plans-root cache/plans/micro_plans \\
        --labels-root data/annotations/standard_labels/micro \\
        --alias-root knowledge_graph/alias \\
        --kg-csv-root knowledge_graph/raw_csv \\
        --output-csv experiments/v7.4_run1/planner_audit_report.csv \\
        --subjects biology chemistry

版本：v1.0
更新：2025-12-31
"""

import sys
import json
import csv
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

# 添加项目根目录到 sys.path
sys.path.append(str(Path(__file__).resolve().parents[2]))


def load_alias_map(alias_root: Path, subject: str) -> Dict[str, Dict[str, any]]:
    """加载 alias 表"""
    alias_file = alias_root / f"{subject}_alias.json"
    if not alias_file.exists():
        return {}
    with open(alias_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_kc_dict(kg_csv_root: Path) -> Dict[str, str]:
    """加载 KC 字典 {kc_id: name}"""
    kc_file = kg_csv_root / "nodes_kc.csv"
    if not kc_file.exists():
        return {}
    
    kc_dict = {}
    with open(kc_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            kc_id = row.get('id', '')
            name = row.get('name', '')
            kc_dict[kc_id] = name
    return kc_dict


def normalize_term(term: str, alias_map: Dict[str, Dict[str, any]]) -> str:
    """术语规范化"""
    term_clean = term.strip().replace(' ', '').lower()
    
    for kc_id, info in alias_map.items():
        canonical = info.get('canonical', '')
        aliases = info.get('aliases', [])
        
        canonical_clean = canonical.replace(' ', '').lower()
        if term_clean == canonical_clean:
            return canonical
        
        for alias in aliases:
            alias_clean = alias.replace(' ', '').lower()
            if term_clean == alias_clean:
                return canonical
    
    return term.strip()


def compute_kc_coverage(plan_kc_names: List[str], 
                        label_kp: List[str], 
                        alias_map: Dict[str, Dict[str, any]]) -> Tuple[float, int, int]:
    """
    计算 KC 覆盖率
    
    Returns:
        (coverage_rate, matched_count, total_kp_count)
    """
    if not label_kp:
        return 1.0, 0, 0
    
    # 规范化 plan KC
    plan_kc_normalized = set()
    for kc_name in plan_kc_names:
        normalized = normalize_term(kc_name, alias_map)
        plan_kc_normalized.add(normalized)
    
    # 规范化 label kp
    label_kp_normalized = set()
    for kp in label_kp:
        normalized = normalize_term(kp, alias_map)
        label_kp_normalized.add(normalized)
    
    # 计算覆盖
    matched = plan_kc_normalized & label_kp_normalized
    coverage = len(matched) / len(label_kp_normalized) if label_kp_normalized else 0.0
    
    return coverage, len(matched), len(label_kp_normalized)


def compute_pi_mentionability(pi_kc_names: List[str], 
                               transcript: str, 
                               alias_map: Dict[str, Dict[str, any]]) -> Tuple[float, int, int]:
    """
    计算 π 可讲述性（π 中的节点在 transcript 中的出现率）
    
    Returns:
        (mentionability_rate, mentioned_count, total_pi_count)
    """
    if not pi_kc_names:
        return 0.0, 0, 0
    
    transcript_lower = transcript.lower()
    mentioned = 0
    
    for kc_name in pi_kc_names:
        # 检查 KC name 是否在 transcript 中
        if kc_name.lower() in transcript_lower:
            mentioned += 1
            continue
        
        # 检查 alias 是否在 transcript 中
        for kc_id, info in alias_map.items():
            if info.get('canonical', '') == kc_name:
                aliases = info.get('aliases', [])
                for alias in aliases:
                    if alias.lower() in transcript_lower:
                        mentioned += 1
                        break
                break
    
    mentionability = mentioned / len(pi_kc_names) if pi_kc_names else 0.0
    return mentionability, mentioned, len(pi_kc_names)


def compute_tp_completeness(plan: Dict) -> Tuple[float, int, int]:
    """
    计算 TP 完整性（TP 与 HAS_CONCEPT 的完整性）
    
    Returns:
        (completeness_rate, has_concept_count, expected_count)
    """
    nodes_tp = plan.get('nodes_tp', [])
    nodes_kc = plan.get('nodes_kc', [])
    edges_has_concept = plan.get('edges_has_concept', [])
    
    if not nodes_tp or not nodes_kc:
        return 0.0, 0, 0
    
    # 期望：每个 TP 至少有一个 HAS_CONCEPT 边
    tp_with_concept = set()
    for edge in edges_has_concept:
        if isinstance(edge, (list, tuple)) and len(edge) >= 2:
            tp_with_concept.add(edge[0])
        elif isinstance(edge, dict):
            tp_with_concept.add(edge.get('from', '') or edge.get('source', ''))
    
    completeness = len(tp_with_concept) / len(nodes_tp) if nodes_tp else 0.0
    return completeness, len(tp_with_concept), len(nodes_tp)


def audit_single_plan(plan_file: Path, 
                      label_file: Path, 
                      alias_map: Dict[str, Dict[str, any]],
                      kc_dict: Dict[str, str]) -> Dict:
    """
    审计单个 plan
    
    Returns:
        审计报告字典
    """
    # 加载 plan
    try:
        with open(plan_file, 'r', encoding='utf-8') as f:
            plan = json.load(f)
    except Exception as e:
        return {
            'status': 'error',
            'error': f'Failed to load plan: {e}'
        }
    
    # 加载 label
    try:
        with open(label_file, 'r', encoding='utf-8') as f:
            label = json.load(f)
    except Exception as e:
        return {
            'status': 'error',
            'error': f'Failed to load label: {e}'
        }
    
    # 提取数据
    plan_kc_ids = plan.get('nodes_kc', [])
    plan_kc_names = plan.get('nodes_kc_name', [])
    if not plan_kc_names:
        # Fallback：从 kc_dict 获取 name
        plan_kc_names = [kc_dict.get(kc_id, kc_id) for kc_id in plan_kc_ids]
    
    pi_kc_ids = plan.get('pi', []) or plan.get('pi_kc', [])
    pi_kc_names = [kc_dict.get(kc_id, kc_id) for kc_id in pi_kc_ids]
    
    label_kp = label.get('kp_plain', []) or label.get('knowledge_points', [])
    if isinstance(label_kp[0] if label_kp else None, dict):
        label_kp = [kp.get('name', '') for kp in label_kp]
    
    transcript = label.get('text_input', '') or label.get('transcript', '')
    
    # 1. KC 覆盖率
    kc_coverage, kc_matched, kc_total = compute_kc_coverage(plan_kc_names, label_kp, alias_map)
    
    # 2. π 可讲述性
    pi_mentionability, pi_mentioned, pi_total = compute_pi_mentionability(pi_kc_names, transcript, alias_map)
    
    # 3. TP 完整性
    tp_completeness, tp_with_concept, tp_total = compute_tp_completeness(plan)
    
    # 4. 其他统计
    edges_based_on = plan.get('edges_based_on', [])
    edges_next = plan.get('edges_next', [])
    
    return {
        'status': 'success',
        'plan_id': plan.get('plan_id', ''),
        'subject': plan.get('subject', ''),
        'video_id': plan.get('video_id', ''),
        'segment_id': plan.get('segment_id', ''),
        'stage': plan.get('stage', ''),
        
        # KC 覆盖率
        'kc_coverage': kc_coverage,
        'kc_matched': kc_matched,
        'kc_total_in_label': kc_total,
        'kc_count_in_plan': len(plan_kc_ids),
        
        # π 可讲述性
        'pi_mentionability': pi_mentionability,
        'pi_mentioned': pi_mentioned,
        'pi_total': pi_total,
        
        # TP 完整性
        'tp_completeness': tp_completeness,
        'tp_with_concept': tp_with_concept,
        'tp_total': tp_total,
        
        # 边统计
        'edges_based_on_count': len(edges_based_on),
        'edges_next_count': len(edges_next),
        
        # 综合评分
        'quality_score': (kc_coverage * 0.5 + pi_mentionability * 0.3 + tp_completeness * 0.2),
    }


def main():
    parser = argparse.ArgumentParser(description="KCVR Planner 质量审计")
    parser.add_argument('--plans-root', type=str, required=True,
                       help='Plans 根目录（cache/plans/micro_plans）')
    parser.add_argument('--labels-root', type=str, required=True,
                       help='标注根目录（data/annotations/standard_labels/micro）')
    parser.add_argument('--alias-root', type=str, required=True,
                       help='Alias 表根目录（knowledge_graph/alias）')
    parser.add_argument('--kg-csv-root', type=str, required=True,
                       help='KG CSV 根目录（knowledge_graph/raw_csv）')
    parser.add_argument('--output-csv', type=str, required=True,
                       help='输出 CSV 文件路径')
    parser.add_argument('--subjects', type=str, nargs='+', default=None,
                       help='指定学科列表（默认全部）')
    
    args = parser.parse_args()
    
    plans_root = Path(args.plans_root)
    labels_root = Path(args.labels_root)
    alias_root = Path(args.alias_root)
    kg_csv_root = Path(args.kg_csv_root)
    output_csv = Path(args.output_csv)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    
    print("="*60)
    print("KCVR Planner 质量审计")
    print("="*60)
    print(f"Plans root: {plans_root}")
    print(f"Labels root: {labels_root}")
    print(f"Output CSV: {output_csv}")
    print()
    
    # 加载 KC 字典
    print("[0/3] Loading KC dictionary...")
    kc_dict = load_kc_dict(kg_csv_root)
    print(f"  Loaded {len(kc_dict)} KC nodes")
    
    # 确定学科列表
    if args.subjects:
        subjects = args.subjects
    else:
        subjects = [d.name for d in plans_root.iterdir() if d.is_dir()]
    
    # 审计结果
    reports = []
    
    # 逐学科审计
    for subject in subjects:
        print(f"\n[{subject}]")
        
        # 加载 alias 表
        alias_map = load_alias_map(alias_root, subject)
        print(f"  Alias map: {len(alias_map)} entries")
        
        subject_plans_root = plans_root / subject
        if not subject_plans_root.exists():
            print(f"  Warning: Plans directory not found: {subject_plans_root}")
            continue
        
        # 遍历所有 plan
        plan_count = 0
        for video_dir in subject_plans_root.iterdir():
            if not video_dir.is_dir():
                continue
            
            for plan_file in video_dir.glob("*.json"):
                # 解析 plan_file 名称
                # 格式：{video_id}__{segment_id}.json
                plan_name = plan_file.stem
                if '__' not in plan_name:
                    continue
                
                video_id, segment_id = plan_name.split('__', 1)
                
                # 查找对应的 label 文件
                # 格式：{video_id}_{stage}.json
                video_prefix = video_id.split('_')[1] if '_' in video_id else video_id
                label_dir = labels_root / subject / video_prefix
                
                # 尝试匹配 stage
                stage_map = {
                    'seg_0001': 'intro',
                    'seg_0002': 'exposition',
                    'seg_0003': 'interaction',
                    'seg_0004': 'conclusion',
                }
                stage = stage_map.get(segment_id, '')
                
                if stage:
                    label_file = label_dir / f"{video_id}_{stage}.json"
                else:
                    # Fallback：查找所有可能的 label 文件
                    label_files = list(label_dir.glob(f"{video_id}_*.json")) if label_dir.exists() else []
                    label_file = label_files[0] if label_files else None
                
                if not label_file or not label_file.exists():
                    print(f"  Warning: Label file not found for {plan_file.name}")
                    continue
                
                # 审计
                report = audit_single_plan(plan_file, label_file, alias_map, kc_dict)
                reports.append(report)
                plan_count += 1
        
        print(f"  Audited {plan_count} plans")
    
    # 写入 CSV
    print(f"\n[{len(subjects)}/{len(subjects)}] Writing results to CSV...")
    
    if reports:
        fieldnames = [
            'status', 'plan_id', 'subject', 'video_id', 'segment_id', 'stage',
            'kc_coverage', 'kc_matched', 'kc_total_in_label', 'kc_count_in_plan',
            'pi_mentionability', 'pi_mentioned', 'pi_total',
            'tp_completeness', 'tp_with_concept', 'tp_total',
            'edges_based_on_count', 'edges_next_count',
            'quality_score', 'error',
        ]
        
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for report in reports:
                # 填充缺失字段
                for field in fieldnames:
                    if field not in report:
                        report[field] = ''
                writer.writerow(report)
        
        print(f"  ✅ Saved to: {output_csv}")
    
    # 打印统计
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    success_reports = [r for r in reports if r.get('status') == 'success']
    
    if success_reports:
        avg_kc_coverage = sum(r['kc_coverage'] for r in success_reports) / len(success_reports)
        avg_pi_mentionability = sum(r['pi_mentionability'] for r in success_reports) / len(success_reports)
        avg_tp_completeness = sum(r['tp_completeness'] for r in success_reports) / len(success_reports)
        avg_quality_score = sum(r['quality_score'] for r in success_reports) / len(success_reports)
        
        print(f"  Total plans: {len(reports)}")
        print(f"  Success: {len(success_reports)}")
        print(f"  Failed: {len(reports) - len(success_reports)}")
        print()
        print(f"  Average KC Coverage: {avg_kc_coverage:.2%}")
        print(f"  Average π Mentionability: {avg_pi_mentionability:.2%}")
        print(f"  Average TP Completeness: {avg_tp_completeness:.2%}")
        print(f"  Average Quality Score: {avg_quality_score:.2%}")
        print()
        
        # 按学科统计
        by_subject = defaultdict(list)
        for r in success_reports:
            by_subject[r['subject']].append(r)
        
        print("  Per-Subject Statistics:")
        for subject, subject_reports in sorted(by_subject.items()):
            avg_kc = sum(r['kc_coverage'] for r in subject_reports) / len(subject_reports)
            avg_pi = sum(r['pi_mentionability'] for r in subject_reports) / len(subject_reports)
            avg_tp = sum(r['tp_completeness'] for r in subject_reports) / len(subject_reports)
            print(f"    {subject:15s}: KC={avg_kc:.2%}, π={avg_pi:.2%}, TP={avg_tp:.2%} (n={len(subject_reports)})")
    
    print("="*60)
    print("✅ Audit completed successfully!")


if __name__ == '__main__':
    main()


