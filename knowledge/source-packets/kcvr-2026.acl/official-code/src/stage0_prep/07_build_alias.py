"""
KCVR Subject Alias 表构建脚本
============================

功能：从 KG 的 KC 节点 + 标注的 knowledge_points + TP 节点自动构建 subject 内 alias 表

构建策略：
1. 从 KG 的 KC 节点提取（最可靠）
2. 从标注的 knowledge_points 提取（覆盖人工标注的变体）
3. 从 TP 节点提取（补充章节级术语）

使用示例：
    python src/stage0_prep/07_build_alias.py \\
        --kg-csv-root knowledge_graph/raw_csv \\
        --labels-root data/annotations/standard_labels \\
        --output-dir knowledge_graph/alias \\
        --subjects biology chemistry

版本：v1.0
更新：2025-12-31
"""

import sys
import json
import csv
import argparse
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

# 添加项目根目录到 sys.path
sys.path.append(str(Path(__file__).resolve().parents[2]))


def extract_aliases_from_definition(definition: str) -> List[str]:
    """
    从定义中提取括号内的别名
    
    例如："限制性内切酶（限制酶）是一种..." -> ["限制酶"]
    
    Args:
        definition: 定义文本
        
    Returns:
        别名列表
    """
    aliases = []
    
    # 匹配中文括号
    matches = re.findall(r'（([^）]+)）', definition)
    aliases.extend(matches)
    
    # 匹配英文括号
    matches = re.findall(r'\(([^)]+)\)', definition)
    aliases.extend(matches)
    
    # 清洗：去除"又称"、"即"等前缀
    cleaned = []
    for alias in aliases:
        alias = alias.strip()
        alias = re.sub(r'^(又称|即|也称|简称|全称)\s*', '', alias)
        if alias and len(alias) < 20:  # 过滤过长的（可能不是别名）
            cleaned.append(alias)
    
    return cleaned


def load_kc_nodes(kg_csv_root: Path, subject: str) -> Dict[str, Dict[str, any]]:
    """
    加载 KC 节点
    
    Args:
        kg_csv_root: KG CSV 根目录
        subject: 学科名
        
    Returns:
        {kc_id: {"name": str, "definition": str, "aliases": [str]}}
    """
    kc_file = kg_csv_root / "nodes_kc.csv"
    
    if not kc_file.exists():
        print(f"  Warning: KC file not found: {kc_file}")
        return {}
    
    kc_nodes = {}
    subject_prefix_map = {
        'biology': 'kc_bio',
        'chemistry': 'kc_chem',
        'chinese': 'kc_chi',
        'english': 'kc_eng',
        'geography': 'kc_geo',
        'history': 'kc_hist',
        'math': 'kc_math',
        'physics': 'kc_phys',
        'politics': 'kc_pol',
        'tech': 'kc_tech',
    }
    subject_prefix = subject_prefix_map.get(subject, f'kc_{subject}')
    
    with open(kc_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            kc_id = row.get('id', '')
            if not kc_id.startswith(subject_prefix):
                continue
            
            name = row.get('name', '').strip()
            definition = row.get('definition', '').strip()
            
            # 从定义中提取别名
            aliases = extract_aliases_from_definition(definition)
            
            # 如果有 alias/synonyms 字段，直接使用
            if 'alias' in row and row['alias']:
                aliases.extend([a.strip() for a in row['alias'].split(';') if a.strip()])
            if 'synonyms' in row and row['synonyms']:
                aliases.extend([a.strip() for a in row['synonyms'].split(';') if a.strip()])
            
            # 去重
            aliases = list(set(aliases))
            
            kc_nodes[kc_id] = {
                'name': name,
                'definition': definition,
                'aliases': aliases,
            }
    
    return kc_nodes


def load_tp_nodes(kg_csv_root: Path, subject: str) -> Dict[str, str]:
    """
    加载 TP 节点
    
    Args:
        kg_csv_root: KG CSV 根目录
        subject: 学科名
        
    Returns:
        {tp_id: name}
    """
    tp_file = kg_csv_root / "nodes_tp.csv"
    
    if not tp_file.exists():
        print(f"  Warning: TP file not found: {tp_file}")
        return {}
    
    tp_nodes = {}
    subject_prefix_map = {
        'biology': 'tp_bio',
        'chemistry': 'tp_chem',
        'chinese': 'tp_chi',
        'english': 'tp_eng',
        'geography': 'tp_geo',
        'history': 'tp_hist',
        'math': 'tp_math',
        'physics': 'tp_phys',
        'politics': 'tp_pol',
        'tech': 'tp_tech',
    }
    subject_prefix = subject_prefix_map.get(subject, f'tp_{subject}')
    
    with open(tp_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tp_id = row.get('id', '')
            if not tp_id.startswith(subject_prefix):
                continue
            
            name = row.get('name', '').strip()
            tp_nodes[tp_id] = name
    
    return tp_nodes


def collect_kp_from_labels(labels_root: Path, subject: str) -> Set[str]:
    """
    从标注中收集 knowledge_points
    
    Args:
        labels_root: 标注根目录
        subject: 学科名
        
    Returns:
        knowledge_points 集合
    """
    kp_set = set()
    
    # 收集 micro
    micro_root = labels_root / 'micro' / subject
    if micro_root.exists():
        for video_dir in micro_root.iterdir():
            if not video_dir.is_dir():
                continue
            for label_file in video_dir.glob("*.json"):
                try:
                    with open(label_file, 'r', encoding='utf-8') as f:
                        label = json.load(f)
                    
                    knowledge_points = label.get('knowledge_points', [])
                    for kp in knowledge_points:
                        if isinstance(kp, dict):
                            name = kp.get('name', '').strip()
                        elif isinstance(kp, str):
                            name = kp.strip()
                        else:
                            continue
                        
                        if name:
                            kp_set.add(name)
                
                except Exception as e:
                    pass
    
    # 收集 macro
    macro_root = labels_root / 'macro' / subject
    if macro_root.exists():
        for video_dir in macro_root.iterdir():
            if not video_dir.is_dir():
                continue
            for label_file in video_dir.glob("*.json"):
                try:
                    with open(label_file, 'r', encoding='utf-8') as f:
                        label = json.load(f)
                    
                    knowledge_points = label.get('knowledge_points', [])
                    for kp in knowledge_points:
                        if isinstance(kp, dict):
                            name = kp.get('name', '').strip()
                        elif isinstance(kp, str):
                            name = kp.strip()
                        else:
                            continue
                        
                        if name:
                            kp_set.add(name)
                
                except Exception as e:
                    pass
    
    return kp_set


def fuzzy_match(text1: str, text2: str, threshold: float = 0.85) -> bool:
    """
    模糊匹配（基于编辑距离）
    
    Args:
        text1: 文本1
        text2: 文本2
        threshold: 相似度阈值
        
    Returns:
        是否匹配
    """
    # 去除空格
    t1 = text1.replace(' ', '').lower()
    t2 = text2.replace(' ', '').lower()
    
    # 完全匹配
    if t1 == t2:
        return True
    
    # 子串匹配
    if t1 in t2 or t2 in t1:
        return True
    
    # 编辑距离（简化版：只计算长度差异）
    len_diff = abs(len(t1) - len(t2))
    max_len = max(len(t1), len(t2))
    if max_len == 0:
        return False
    
    similarity = 1 - (len_diff / max_len)
    return similarity >= threshold


def build_alias_map(kc_nodes: Dict[str, Dict[str, any]], 
                    tp_nodes: Dict[str, str], 
                    kp_set: Set[str]) -> Dict[str, Dict[str, any]]:
    """
    构建 alias 表
    
    Args:
        kc_nodes: KC 节点
        tp_nodes: TP 节点
        kp_set: 标注中的 knowledge_points
        
    Returns:
        {kc_id: {"canonical": str, "aliases": [str]}}
    """
    alias_map = {}
    
    for kc_id, kc_info in kc_nodes.items():
        canonical = kc_info['name']
        aliases = set(kc_info['aliases'])
        
        # 从 kp_set 中查找匹配
        for kp in kp_set:
            if fuzzy_match(canonical, kp, threshold=0.90):
                if kp != canonical:
                    aliases.add(kp)
        
        # 从 tp_nodes 中查找匹配（阈值更低，因为章节名可能更长）
        for tp_name in tp_nodes.values():
            if fuzzy_match(canonical, tp_name, threshold=0.85):
                if tp_name != canonical and len(tp_name) < 30:  # 过滤过长的章节名
                    aliases.add(tp_name)
        
        # 去重并排序
        aliases = sorted(list(aliases))
        
        alias_map[kc_id] = {
            'canonical': canonical,
            'aliases': aliases,
        }
    
    return alias_map


def main():
    parser = argparse.ArgumentParser(description="KCVR Subject Alias 表构建")
    parser.add_argument('--kg-csv-root', type=str, required=True,
                       help='KG CSV 根目录（knowledge_graph/raw_csv）')
    parser.add_argument('--labels-root', type=str, required=True,
                       help='标注根目录（data/annotations/standard_labels）')
    parser.add_argument('--output-dir', type=str, required=True,
                       help='输出目录（knowledge_graph/alias）')
    parser.add_argument('--subjects', type=str, nargs='+', default=None,
                       help='指定学科列表（默认全部）')
    
    args = parser.parse_args()
    
    kg_csv_root = Path(args.kg_csv_root)
    labels_root = Path(args.labels_root)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("="*60)
    print("KCVR Subject Alias 表构建")
    print("="*60)
    print(f"KG CSV root: {kg_csv_root}")
    print(f"Labels root: {labels_root}")
    print(f"Output dir: {output_dir}")
    print()
    
    # 确定学科列表
    if args.subjects:
        subjects = args.subjects
    else:
        micro_root = labels_root / 'micro'
        subjects = [d.name for d in micro_root.iterdir() if d.is_dir()] if micro_root.exists() else []
    
    # 逐学科构建
    for subject in subjects:
        print(f"[{subject}]")
        
        # 1. 加载 KC 节点
        print(f"  [1/4] Loading KC nodes...")
        kc_nodes = load_kc_nodes(kg_csv_root, subject)
        print(f"    Loaded {len(kc_nodes)} KC nodes")
        
        # 2. 加载 TP 节点
        print(f"  [2/4] Loading TP nodes...")
        tp_nodes = load_tp_nodes(kg_csv_root, subject)
        print(f"    Loaded {len(tp_nodes)} TP nodes")
        
        # 3. 收集标注中的 knowledge_points
        print(f"  [3/4] Collecting knowledge_points from labels...")
        kp_set = collect_kp_from_labels(labels_root, subject)
        print(f"    Collected {len(kp_set)} unique knowledge_points")
        
        # 4. 构建 alias 表
        print(f"  [4/4] Building alias map...")
        alias_map = build_alias_map(kc_nodes, tp_nodes, kp_set)
        
        # 统计
        total_aliases = sum(len(info['aliases']) for info in alias_map.values())
        print(f"    Built alias map: {len(alias_map)} KC nodes, {total_aliases} aliases")
        
        # 写入
        output_file = output_dir / f"{subject}_alias.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(alias_map, f, ensure_ascii=False, indent=2)
        
        print(f"  ✅ Saved to: {output_file}")
        print()
    
    print("="*60)
    print("✅ Alias map construction completed successfully!")
    print("="*60)


if __name__ == '__main__':
    main()


