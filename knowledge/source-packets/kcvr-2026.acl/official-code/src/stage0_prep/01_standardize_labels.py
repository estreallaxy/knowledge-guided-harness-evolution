"""
KCVR 数据清洗与标准化脚本
========================

功能：
1. 清洗 standard_labels 中的 markdown 格式、统一标点与空白
2. 术语规范化（基于 alias 表）
3. 在原 JSON 中新增 canonical 字段（summary_plain、objectives_plain、kp_plain）

使用示例：
    python src/stage0_prep/01_standardize_labels.py \\
        --labels-root data/annotations/standard_labels \\
        --alias-root knowledge_graph/alias \\
        --output-root data/annotations/standard_labels \\
        --dry-run

版本：v1.0
更新：2025-12-31
"""

import sys
import json
import argparse
import re
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

# 添加项目根目录到 sys.path
sys.path.append(str(Path(__file__).resolve().parents[2]))


def clean_text(text: str) -> str:
    """
    清洗文本：去除 markdown 格式、统一标点与空白
    
    Args:
        text: 原始文本
        
    Returns:
        清洗后的文本
    """
    if not text:
        return ""
    
    # 去除 ### 标题符号
    text = re.sub(r'###\s*', '', text)
    
    # 去除 ** 加粗符号
    text = re.sub(r'\*\*', '', text)
    
    # 去除 【】 和 [] 框架符号（但保留内容）
    text = re.sub(r'[【】\[\]]', '', text)
    
    # 去除 markdown 列表符号
    text = re.sub(r'^\s*[-\*]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    
    # 统一标点：全角转半角（除中文逗号、句号、顿号）
    # 保留中文标点：，。、；：""''
    # 转换英文标点：,.:;!?()
    replacements = {
        '，': '，',  # 保留
        '。': '。',  # 保留
        '、': '、',  # 保留
        '；': ';',
        '：': ':',
        '！': '!',
        '？': '?',
        '（': '(',
        '）': ')',
        '"': '"',
        '"': '"',
        ''': "'",
        ''': "'",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # 去除重复空格（保留单个空格）
    text = re.sub(r' +', ' ', text)
    
    # 去除多余换行（保留段落结构，最多 2 个连续换行）
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    
    # 去除首尾空白
    text = text.strip()
    
    return text


def normalize_term(term: str, alias_map: Dict[str, Dict[str, Any]]) -> str:
    """
    术语规范化：将术语映射到 canonical name
    
    Args:
        term: 原始术语
        alias_map: alias 表 {kc_id: {"canonical": str, "aliases": [str]}}
        
    Returns:
        规范化后的术语（如果找到映射）或原术语
    """
    term_clean = term.strip()
    
    # 遍历 alias 表，查找匹配
    for kc_id, info in alias_map.items():
        canonical = info.get('canonical', '')
        aliases = info.get('aliases', [])
        
        # 完全匹配
        if term_clean == canonical:
            return canonical
        if term_clean in aliases:
            return canonical
        
        # 模糊匹配（去除空格后）
        term_no_space = term_clean.replace(' ', '')
        canonical_no_space = canonical.replace(' ', '')
        if term_no_space == canonical_no_space:
            return canonical
        for alias in aliases:
            alias_no_space = alias.replace(' ', '')
            if term_no_space == alias_no_space:
                return canonical
    
    # 未找到映射，返回原术语
    return term_clean


def clean_micro_label(label: Dict[str, Any], alias_map: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    清洗 micro 标注
    
    Args:
        label: 原始标注 JSON
        alias_map: alias 表
        
    Returns:
        添加了 canonical 字段的标注 JSON
    """
    # 清洗摘要
    summary_gt = label.get('summary_gt', '') or label.get('summary_target', '')
    label['summary_plain'] = clean_text(summary_gt)
    
    # 清洗学习目标
    objectives_gt = label.get('objectives_gt', []) or label.get('learning_objectives', [])
    if isinstance(objectives_gt, str):
        objectives_gt = [obj.strip() for obj in re.split(r'[；;。.\n]', objectives_gt) if obj.strip()]
    label['objectives_plain'] = [clean_text(obj) for obj in objectives_gt]
    
    # 清洗知识点
    knowledge_points = label.get('knowledge_points', [])
    kp_plain = []
    for kp in knowledge_points:
        if isinstance(kp, dict):
            name = kp.get('name', '')
        elif isinstance(kp, str):
            name = kp
        else:
            continue
        
        # 清洗并规范化
        name_clean = clean_text(name)
        name_normalized = normalize_term(name_clean, alias_map)
        kp_plain.append(name_normalized)
    
    label['kp_plain'] = kp_plain
    
    return label


def clean_macro_label(label: Dict[str, Any], alias_map: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    清洗 macro 标注
    
    Args:
        label: 原始标注 JSON
        alias_map: alias 表
        
    Returns:
        添加了 canonical 字段的标注 JSON
    """
    # 清洗教育摘要
    summary_edu_gt = label.get('summary_edu_gt', '')
    label['summary_edu_plain'] = clean_text(summary_edu_gt)
    
    # 清洗整体摘要
    overall_summary_gt = label.get('overall_summary_gt', '')
    label['overall_summary_plain'] = clean_text(overall_summary_gt)
    
    # 清洗学习目标
    learning_objectives = label.get('learning_objectives', [])
    if isinstance(learning_objectives, str):
        learning_objectives = [obj.strip() for obj in re.split(r'[；;。.\n]', learning_objectives) if obj.strip()]
    label['objectives_plain'] = [clean_text(obj) for obj in learning_objectives]
    
    # 清洗知识点
    knowledge_points = label.get('knowledge_points', [])
    kp_plain = []
    for kp in knowledge_points:
        if isinstance(kp, dict):
            name = kp.get('name', '')
        elif isinstance(kp, str):
            name = kp
        else:
            continue
        
        # 清洗并规范化
        name_clean = clean_text(name)
        name_normalized = normalize_term(name_clean, alias_map)
        kp_plain.append(name_normalized)
    
    label['kp_plain'] = kp_plain
    
    return label


def load_alias_map(alias_root: Path, subject: str) -> Dict[str, Dict[str, Any]]:
    """
    加载 subject 的 alias 表
    
    Args:
        alias_root: alias 根目录
        subject: 学科名
        
    Returns:
        alias 表 {kc_id: {"canonical": str, "aliases": [str]}}
    """
    alias_file = alias_root / f"{subject}_alias.json"
    
    if not alias_file.exists():
        print(f"  Warning: Alias file not found for {subject}: {alias_file}")
        return {}
    
    with open(alias_file, 'r', encoding='utf-8') as f:
        alias_map = json.load(f)
    
    return alias_map


def main():
    parser = argparse.ArgumentParser(description="KCVR 数据清洗与标准化")
    parser.add_argument('--labels-root', type=str, required=True,
                       help='标注根目录（data/annotations/standard_labels）')
    parser.add_argument('--alias-root', type=str, default='knowledge_graph/alias',
                       help='Alias 表根目录')
    parser.add_argument('--output-root', type=str, default=None,
                       help='输出根目录（默认覆盖原文件）')
    parser.add_argument('--dry-run', action='store_true',
                       help='Dry run：只打印统计，不写入文件')
    parser.add_argument('--subjects', type=str, nargs='+', default=None,
                       help='指定学科列表（默认全部）')
    
    args = parser.parse_args()
    
    labels_root = Path(args.labels_root)
    alias_root = Path(args.alias_root)
    output_root = Path(args.output_root) if args.output_root else labels_root
    
    print("="*60)
    print("KCVR 数据清洗与标准化")
    print("="*60)
    print(f"Labels root: {labels_root}")
    print(f"Alias root: {alias_root}")
    print(f"Output root: {output_root}")
    print(f"Dry run: {args.dry_run}")
    print()
    
    # 统计
    stats = defaultdict(lambda: {'micro': 0, 'macro': 0})
    
    # 处理 micro
    micro_root = labels_root / 'micro'
    if micro_root.exists():
        print("[1/2] Processing micro labels...")
        
        subjects = args.subjects if args.subjects else [d.name for d in micro_root.iterdir() if d.is_dir()]
        
        for subject in subjects:
            subject_dir = micro_root / subject
            if not subject_dir.exists():
                continue
            
            # 加载 alias 表
            alias_map = load_alias_map(alias_root, subject)
            
            for video_dir in subject_dir.iterdir():
                if not video_dir.is_dir():
                    continue
                
                for label_file in video_dir.glob("*.json"):
                    try:
                        with open(label_file, 'r', encoding='utf-8') as f:
                            label = json.load(f)
                        
                        # 清洗
                        label_clean = clean_micro_label(label, alias_map)
                        
                        # 写入
                        if not args.dry_run:
                            output_file = output_root / 'micro' / subject / video_dir.name / label_file.name
                            output_file.parent.mkdir(parents=True, exist_ok=True)
                            with open(output_file, 'w', encoding='utf-8') as f:
                                json.dump(label_clean, f, ensure_ascii=False, indent=2)
                        
                        stats[subject]['micro'] += 1
                    
                    except Exception as e:
                        print(f"  Error processing {label_file}: {e}")
        
        print(f"  Processed {sum(s['micro'] for s in stats.values())} micro labels")
    
    # 处理 macro
    macro_root = labels_root / 'macro'
    if macro_root.exists():
        print("\n[2/2] Processing macro labels...")
        
        subjects = args.subjects if args.subjects else [d.name for d in macro_root.iterdir() if d.is_dir()]
        
        for subject in subjects:
            subject_dir = macro_root / subject
            if not subject_dir.exists():
                continue
            
            # 加载 alias 表
            alias_map = load_alias_map(alias_root, subject)
            
            for video_dir in subject_dir.iterdir():
                if not video_dir.is_dir():
                    continue
                
                for label_file in video_dir.glob("*.json"):
                    try:
                        with open(label_file, 'r', encoding='utf-8') as f:
                            label = json.load(f)
                        
                        # 清洗
                        label_clean = clean_macro_label(label, alias_map)
                        
                        # 写入
                        if not args.dry_run:
                            output_file = output_root / 'macro' / subject / video_dir.name / label_file.name
                            output_file.parent.mkdir(parents=True, exist_ok=True)
                            with open(output_file, 'w', encoding='utf-8') as f:
                                json.dump(label_clean, f, ensure_ascii=False, indent=2)
                        
                        stats[subject]['macro'] += 1
                    
                    except Exception as e:
                        print(f"  Error processing {label_file}: {e}")
        
        print(f"  Processed {sum(s['macro'] for s in stats.values())} macro labels")
    
    # 打印统计
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for subject, counts in sorted(stats.items()):
        print(f"  {subject:15s}: {counts['micro']:3d} micro, {counts['macro']:3d} macro")
    print(f"  {'TOTAL':15s}: {sum(s['micro'] for s in stats.values()):3d} micro, {sum(s['macro'] for s in stats.values()):3d} macro")
    print("="*60)
    
    if args.dry_run:
        print("\n⚠️  Dry run mode: No files were modified.")
    else:
        print("\n✅ Data cleaning completed successfully!")


if __name__ == '__main__':
    main()
