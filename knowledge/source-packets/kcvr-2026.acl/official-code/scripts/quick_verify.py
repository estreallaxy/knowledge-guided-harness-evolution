#!/usr/bin/env python3
# Quick verification script for code functionality
# Tests data loading, plan loading, and basic metric computation

import sys
from pathlib import Path
import json
import argparse

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.utils.metric_utils import load_ctl_resources, load_kg_edges
from src.stage1_micro.plan_utils import serialize_plan, PlanSerializeConfig


def verify_data_loading(data_root: Path, kg_root: Path):
    """Verify that data files can be loaded correctly."""
    print("Verifying data loading...")
    
    # Check knowledge graph files
    kg_files = ['nodes_kc.csv', 'nodes_tp.csv', 'relations.csv']
    for fname in kg_files:
        kg_file = kg_root / fname
        if kg_file.exists():
            print(f"Found: {kg_file}")
        else:
            print(f"Missing: {kg_file}")
            return False
    
    # Check example annotations
    math_labels = data_root / 'annotations' / 'standard_labels' / 'micro' / 'math'
    if math_labels.exists():
        json_files = list(math_labels.glob('**/*.json'))
            print(f"Found {len(json_files)} annotation files in math/")
        if len(json_files) > 0:
            # Try loading one
            try:
                with open(json_files[0], 'r', encoding='utf-8') as f:
                    sample = json.load(f)
                required_fields = ['summary_gt', 'objectives_gt']
                missing = [f for f in required_fields if f not in sample]
                if missing:
                    print(f"  Warning: Missing fields in sample: {missing}")
                else:
                    print(f"  Sample file structure valid")
            except Exception as e:
                print(f"  ✗ Error loading sample: {e}")
                return False
    else:
        print(f"✗ Missing: {math_labels}")
        return False
    
    # Check plans
    math_plans = Path('cache/plans/micro_plans/math')
    if math_plans.exists():
        plan_files = list(math_plans.glob('**/*.json'))
        print(f"✓ Found {len(plan_files)} plan files in math/")
        if len(plan_files) > 0:
            try:
                with open(plan_files[0], 'r', encoding='utf-8') as f:
                    plan = json.load(f)
                required_fields = ['kc_nodes', 'pi', 'edges_based_on']
                missing = [f for f in required_fields if f not in plan]
                if missing:
                    print(f"  ⚠ Missing fields in plan: {missing}")
                else:
                    print(f"  ✓ Plan file structure valid")
            except Exception as e:
                print(f"  ✗ Error loading plan: {e}")
                return False
    else:
        print(f"⚠ Plans directory not found (may need to generate)")
    
    print("\nData loading verification complete")
    return True


def verify_metrics(kg_root: Path):
    """Verify that metrics can be computed."""
    print("\nVerifying metrics computation...")
    
    try:
        # Try loading CTL resources
        ctl_resources = load_ctl_resources(kg_root, subject='math')
        print("CTL resources loaded")
        
        # Try loading KG edges
        kg_edges = load_kg_edges(kg_root)
        print(f"KG edges loaded ({len(kg_edges.based_on)} BASED_ON edges)")
        
        # Test metric computation
        from src.utils.metric_utils import compute_rouge
        
        pred = "这是一个测试摘要。"
        ref = "这是一个测试摘要。"
        
        rouge_scores = compute_rouge(pred, ref)
        print(f"ROUGE computation works: R1={rouge_scores['rouge1']:.3f}")
        
        print("Basic metrics computation verified")
        
    except Exception as e:
        print(f"✗ Error in metrics verification: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\nMetrics verification complete")
    return True


def verify_plan_serialization(kg_root: Path):
    """Verify plan serialization works."""
    print("\nVerifying plan serialization...")
    
    math_plans = Path('cache/plans/micro_plans/math')
    if not math_plans.exists():
        print("Plans directory not found, skipping plan verification")
        return True
    
    plan_files = list(math_plans.glob('**/*.json'))
    if len(plan_files) == 0:
        print("No plan files found, skipping plan verification")
        return True
    
    try:
        # Load ID mappings
        import csv
        id2kc = {}
        kc_csv = kg_root / 'nodes_kc.csv'
        if kc_csv.exists():
            with open(kc_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rid = row.get('id', '').strip()
                    name = row.get('name', '').strip()
                    if rid and name:
                        id2kc[rid] = name
        
        id2tp = {}
        tp_csv = kg_root / 'nodes_tp.csv'
        if tp_csv.exists():
            with open(tp_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rid = row.get('id', '').strip()
                    name = row.get('name', '').strip()
                    if rid and name:
                        id2tp[rid] = name
        
        # Load and serialize a plan
        with open(plan_files[0], 'r', encoding='utf-8') as f:
            plan = json.load(f)
        
        cfg = PlanSerializeConfig()
        plan_text = serialize_plan(plan, id2kc, id2tp, cfg)
        
        if plan_text and len(plan_text) > 0:
            print(f"Plan serialization works (output length: {len(plan_text)})")
        else:
            print("Error: Plan serialization produced empty output")
            return False
            
    except Exception as e:
        print(f"✗ Error in plan serialization: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\nPlan serialization verification complete")
    return True


def main():
    parser = argparse.ArgumentParser(description="Quick verification of code functionality")
    parser.add_argument('--data-root', type=str, default='data',
                       help='Root directory for data')
    parser.add_argument('--kg-root', type=str, default='knowledge_graph/raw_csv',
                       help='Root directory for knowledge graph CSV files')
    
    args = parser.parse_args()
    
    data_root = Path(args.data_root)
    kg_root = Path(args.kg_root)
    
    print("\nKCVR Code Verification\n")
    
    all_ok = True
    
    # Run verifications
    all_ok &= verify_data_loading(data_root, kg_root)
    all_ok &= verify_metrics(kg_root)
    all_ok &= verify_plan_serialization(kg_root)
    
    print("\n" + "-" * 60)
    if all_ok:
        print("All verifications passed!")
        return 0
    else:
        print("Some verifications failed. Please check errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())

