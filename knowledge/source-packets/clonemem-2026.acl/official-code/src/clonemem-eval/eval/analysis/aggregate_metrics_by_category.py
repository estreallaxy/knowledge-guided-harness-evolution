import json
import argparse
import numpy as np
import os
import sys
import pandas as pd
from pathlib import Path
from collections import defaultdict
from tqdm import tqdm
from fnmatch import fnmatch

# Add project root to Python path
PROJECT_ROOT = os.path.expanduser("~/playground/AgentMem/clonemem_adaptation")
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def parse_args():
    parser = argparse.ArgumentParser(description="Aggregate metrics by question type and dimension across all persons")
    parser.add_argument('--qa_file', type=str, 
                        default='data/new_data/all_users_benchmark_en.json',
                        help='Input file containing all users QA items')
    parser.add_argument('--method_name', type=str, default='flatten')
    parser.add_argument('--retrieval_pattern', type=str, default='*merge_raw-use_chunk*', help='glob pattern to filter retrieval result files')
    parser.add_argument('--generation_pattern', type=str, default='*top10*merge_raw-use_chunk*', help='glob pattern to filter generation result files')
    parser.add_argument('--out_dir', type=str, default=None,
                        help='Output directory to save aggregated results')
    return parser.parse_args()


def load_all_qa_data(qa_file):
    """
    Load all users' QA data and create mappings.
    Returns: 
        - user_qa_map: {user_id: {qa_id: qa_item}}
        - user_info: {user_id: person_name}
    """
    with open(qa_file, 'r') as f:
        all_users_data = json.load(f)
    
    user_qa_map = {}
    user_info = {}
    
    for user_data in all_users_data:
        user_id = user_data['person_id']
        person_name = user_data['person_name']
        user_info[user_id] = person_name
        
        qa_items = user_data['qa_items']
        user_qa_map[user_id] = {item['id']: item for item in qa_items}
    
    return user_qa_map, user_info


def compute_metrics_for_k(retrieved_chunk_ids, evidence_refs, k):
    """
    Compute recall metrics for a single query at a specific K.
    (Copied from compute_auto_metrics_for_clonemem.py)
    
    Args:
        retrieved_chunk_ids: list of chunk IDs ordered by rank
        evidence_refs: list of evidence objects from ground truth
        k: cutoff value
    
    Returns:
        tuple of (recall_all_all, recall_all_any, recall_any_all, recall_any_any, recall_flat)
    """
    # Cut off at K
    top_k_ids = set(retrieved_chunk_ids[:k])
    
    # Pre-calculate hits for each evidence
    evidence_status = []  # List of dicts { 'all_found': bool, 'any_found': bool }
    
    all_gt_media_ids = set()
    
    for ev in evidence_refs:
        media_ids = ev.get('related_media_id', [])
        if not media_ids:
            continue
            
        # Add to flat set
        for mid in media_ids:
            all_gt_media_ids.add(mid)
            
        # Check conditions
        found_count = sum(1 for mid in media_ids if mid in top_k_ids)
        
        evidence_status.append({
            'all_found': found_count == len(media_ids),
            'any_found': found_count > 0
        })

    if not evidence_status:
        # If no evidence refs, return zeros
        if not all_gt_media_ids:
            return 0.0, 0.0, 0.0, 0.0, 0.0
        return 0.0, 0.0, 0.0, 0.0, 0.0

    # 1. Recall-Flat: Proportion of all unique ground truth media IDs found
    flat_found_count = sum(1 for mid in all_gt_media_ids if mid in top_k_ids)
    recall_flat = flat_found_count / len(all_gt_media_ids) if all_gt_media_ids else 0.0

    # 2. Recall-All-All: All evidences must have ALL media IDs found
    recall_all_all = 1.0 if all(e['all_found'] for e in evidence_status) else 0.0

    # 3. Recall-All-Any: All evidences must have AT LEAST ONE media ID found
    recall_all_any = 1.0 if all(e['any_found'] for e in evidence_status) else 0.0

    # 4. Recall-Any-All: At least one evidence must have ALL media IDs found
    recall_any_all = 1.0 if any(e['all_found'] for e in evidence_status) else 0.0

    # 5. Recall-Any-Any: At least one evidence must have AT LEAST ONE media ID found
    recall_any_any = 1.0 if any(e['any_found'] for e in evidence_status) else 0.0

    return recall_all_all, recall_all_any, recall_any_all, recall_any_any, recall_flat


def extract_user_id_from_filename(filename):
    """Extract user_id from recall or llm metric filename."""
    # Recall format: recall_metrics_周瑜_default_9fdf4fb7-c6d8-4fb1-9e01-581d5b85d84a_contriever.json
    # LLM format: 周瑜_llm_judge_周瑜_generation_top5_default_9fdf4fb7-c6d8-4fb1-9e01-581d5b85d84a_contriever
    
    parts = filename.split('_')
    
    # Find the UUID pattern (should be 36 characters with format 8-4-4-4-12)
    for part in parts:
        # Check if it looks like a UUID
        if len(part) == 36 and part.count('-') == 4:
            # Verify format: 8-4-4-4-12
            uuid_parts = part.split('-')
            if (len(uuid_parts) == 5 and 
                len(uuid_parts[0]) == 8 and 
                len(uuid_parts[1]) == 4 and 
                len(uuid_parts[2]) == 4 and 
                len(uuid_parts[3]) == 4 and 
                len(uuid_parts[4]) == 12):
                return part
    raise ValueError(f"Could not extract user_id from filename: {filename}")


def load_recall_metrics(recall_dir, pattern=''):
    """
    Load all recall metrics files.
    Args:
        recall_dir: Directory containing recall metrics files
        pattern: Optional pattern to filter filenames
    Returns: {user_id: recall_metrics_dict}
    """
    recall_metrics = {}
    
    if not os.path.exists(recall_dir):
        raise ValueError(f"Recall metrics directory not found: {recall_dir}")
    
    for filename in os.listdir(recall_dir):
        if filename.startswith('recall_metrics_') and filename.endswith('.json'):
            # Apply pattern filter if provided (glob-style matching)
            if pattern and not fnmatch(filename, pattern):
                continue
            
            filepath = os.path.join(recall_dir, filename)
            user_id = extract_user_id_from_filename(filename)
            
            if user_id:
                with open(filepath, 'r') as f:
                    recall_metrics[user_id] = json.load(f)
    
    return recall_metrics


def load_retrieval_results(retrieval_dir, pattern=''):
    """
    Load all retrieval result files (containing ranked_items per question).
    Args:
        retrieval_dir: Directory containing retrieval results files
        pattern: Optional pattern to filter filenames
    Returns: {user_id: retrieval_results_dict}
    """
    retrieval_results = {}
    count = 0
    
    if not os.path.exists(retrieval_dir):
        raise ValueError(f"Retrieval directory not found: {retrieval_dir}")
    
    # Look for JSON files that contain retrieval results
    # Expected format: default_<user_id>_<model>.json
    for filename in os.listdir(retrieval_dir):
        if filename.endswith('.json') and 'default_' in filename:
            # Apply pattern filter if provided (glob-style matching)
            if pattern and not fnmatch(filename, pattern):
                continue
            
            filepath = os.path.join(retrieval_dir, filename)
            try:
                user_id = extract_user_id_from_filename(filename)
                
                if user_id:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        count += 1
                        # Handle both formats: direct dict or {'results': dict}
                        if isinstance(data, dict):
                            if 'results' in data:
                                retrieval_results[user_id] = data['results']
                            else:
                                retrieval_results[user_id] = data
            except (ValueError, json.JSONDecodeError) as e:
                # Skip files that don't match expected format
                raise
    assert count == 10, f"Expected 10 retrieval files, but found {count}"
    return retrieval_results


def load_generation_results(generation_dir, pattern=''):
    """
    Load all generation result files (containing choices and predictions per question).
    Args:
        generation_dir: Directory containing generation results files
        pattern: Optional pattern to filter filenames
    Returns: {user_id: generation_results_dict}
    """
    generation_results = {} 
    count = 0
    
    if not os.path.exists(generation_dir):
        raise ValueError(f"Generation directory not found: {generation_dir}")
    
    # Look for generation JSON files
    # Expected format: <person_name>_generation_top<k>_default_<user_id>_<model>.json
    for filename in os.listdir(generation_dir):
        if filename.endswith('.json') and 'generation_' in filename and not filename.startswith('.'):
            # Apply pattern filter if provided (glob-style matching)
            if pattern and not fnmatch(filename, pattern):
                continue
            
            filepath = os.path.join(generation_dir, filename)
            try:
                user_id = extract_user_id_from_filename(filename)
                
                if user_id:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        count += 1
                        # Normalize to dict format if needed
                        if isinstance(data, dict):
                            # Convert to {qa_id: item} format if not already
                            normalized = {}
                            for key, item in data.items():
                                if isinstance(item, dict):
                                    qa_id = item.get('id', key)
                                    normalized[qa_id] = item
                            generation_results[user_id] = normalized
            except (ValueError, json.JSONDecodeError) as e:
                # Skip files that don't match expected format
                continue
    assert count == 10, f"Expected 10 generation files, but found {count}"
    return generation_results


def load_llm_metrics(llm_dir, pattern=''):
    """
    Load all LLM judge metrics files.
    Args:
        llm_dir: Directory containing LLM metrics files
        pattern: Optional pattern to filter filenames
    Returns: {user_id: llm_metrics_dict}
    """
    llm_metrics = {}
    
    if not os.path.exists(llm_dir):
        raise ValueError(f"LLM metrics directory not found: {llm_dir}")
    
    for filename in os.listdir(llm_dir):
        if 'llm_judge' in filename:
            # Apply pattern filter if provided (glob-style matching)
            if pattern and not fnmatch(filename, pattern):
                continue
            
            filepath = os.path.join(llm_dir, filename)
            user_id = extract_user_id_from_filename(filename)
            
            if user_id:
                with open(filepath, 'r') as f:
                    llm_metrics[user_id] = json.load(f)
    assert len(llm_metrics) == 10, f"Expected 10 LLM metrics files, but found {len(llm_metrics)}"
    return llm_metrics


def aggregate_metrics_by_category(user_qa_map, retrieval_results_map, generation_results_map, llm_metrics_map, category_key):
    """
    Aggregate metrics by a specific category (question_type or dimension).
    Recomputes recall metrics per question from retrieval results.
    Recomputes choice accuracy per question from generation results.
    
    Args:
        user_qa_map: {user_id: {qa_id: qa_item}}
        retrieval_results_map: {user_id: {qa_id: retrieval_result}}
        generation_results_map: {user_id: {qa_id: generation_result}}
        llm_metrics_map: {user_id: llm_metrics}
        category_key: 'question_type' or 'dimension'
    
    Returns:
        DataFrame with aggregated metrics
    """
    # Storage for metrics by category
    category_metrics = defaultdict(lambda: {
        # Recall metrics @k10
        'recall_all_all_k10': [],
        'recall_all_any_k10': [],
        'recall_any_all_k10': [],
        'recall_any_any_k10': [],
        'recall_flat_k10': [],
        # Recall metrics @k20
        'recall_all_all_k20': [],
        'recall_all_any_k20': [],
        'recall_any_all_k20': [],
        'recall_any_any_k20': [],
        'recall_flat_k20': [],
        # LLM metrics
        'choice_accuracy': [],
        'QA_consistency_score': [],
        'QA_consistency_score_norm': [],
        'Mem_recall': [],
        'Mem_recall_norm': [],
        'Mem_helpful_score': [],
        'Mem_helpful_score_norm': [],
        'qa_hallucination_rate': [],
        'qa_perfect_rate': [],
    })
    
    # Track which QA items have metrics available
    category_qa_counts = defaultdict(int)
    
    # K values for recall computation
    ks = [10, 20]
    
    # Iterate through all users
    for user_id, qa_items in tqdm(user_qa_map.items(), desc=f"Aggregating by {category_key}"):
        # Get this user's retrieval results, generation results, and LLM metrics
        user_retrieval = retrieval_results_map.get(user_id, {})
        user_generation = generation_results_map.get(user_id, {})
        user_llm = llm_metrics_map.get(user_id, {})
        
        if not user_retrieval:
            print(f"  ⚠️  No retrieval results for user {user_id}, skipping")
            continue
        
        if not user_generation:
            print(f"  ⚠️  No generation results for user {user_id}, skipping")
            continue
        
        if not user_llm:
            print(f"  ⚠️  No LLM metrics for user {user_id}, skipping")
            continue
        
        # Get detailed LLM results per QA
        detailed_llm = user_llm.get('detailed_llm_results', {})
        
        # Track metrics per category for this user
        user_category_metrics = defaultdict(lambda: {
            'qa_ids': [],
            'llm_data': [],
        })
        
        # Go through each QA item
        for qa_id, qa_item in qa_items.items():
            category_value = qa_item.get(category_key)
            
            if not category_value:
                continue
            
            category_qa_counts[category_value] += 1
            
            # Check if we have retrieval results for this question
            if qa_id not in user_retrieval:
                continue
            
            retrieval_result = user_retrieval[qa_id]
            
            # Extract ranked chunk IDs from retrieval results
            ranked_items = retrieval_result.get('ranked_items', [])
            ranked_chunk_ids = [
                item['chunk_id'] 
                for item in ranked_items 
                if item.get('res_type') == 'chunk' and 'chunk_id' in item
            ]
            
            # Get ground truth evidence for this question
            evidence_refs = qa_item.get('evidence', [])
            
            if not evidence_refs:
                continue
            
            # Compute recall metrics for this specific question at each K
            for k in ks:
                r_aa, r_aa_ny, r_ny_aa, r_ny_ny, r_flat = compute_metrics_for_k(
                    ranked_chunk_ids, evidence_refs, k
                )
                
                # Add to category metrics
                category_metrics[category_value][f'recall_all_all_k{k}'].append(r_aa)
                category_metrics[category_value][f'recall_all_any_k{k}'].append(r_aa_ny)
                category_metrics[category_value][f'recall_any_all_k{k}'].append(r_ny_aa)
                category_metrics[category_value][f'recall_any_any_k{k}'].append(r_ny_ny)
                category_metrics[category_value][f'recall_flat_k{k}'].append(r_flat)
            
            # Store LLM metrics for this QA if available
            if qa_id in detailed_llm:
                llm_result = detailed_llm[qa_id]
                
                if 'QA_consistency_score' in llm_result:
                    qa_score = llm_result['QA_consistency_score']
                    
                    # Track hallucination and perfect rates per question
                    category_metrics[category_value]['qa_hallucination_rate'].append(1.0 if qa_score == 0 else 0.0)
                    category_metrics[category_value]['qa_perfect_rate'].append(1.0 if qa_score == 3 else 0.0)
                    # category_metrics[category_value]['QA_consistency_score_norm'].append(qa_score / 3.0)
                
                    # NOTE map consistency 0/1 -> 0, 2 -> 1, 3 -> 2
                    mapping = {0: 0, 1: 0, 2: 1, 3: 2}
                    qa_score = mapping[qa_score]
                    category_metrics[category_value]['QA_consistency_score_norm'].append(qa_score / 2.0)
                if 'Mem_recall' in llm_result:
                    mem_recall = llm_result['Mem_recall']
                    category_metrics[category_value]['Mem_recall'].append(mem_recall)
                    category_metrics[category_value]['Mem_recall_norm'].append(mem_recall)
                
                if 'Mem_helpful_score' in llm_result:
                    helpful_score = llm_result['Mem_helpful_score']
                    category_metrics[category_value]['Mem_helpful_score'].append(helpful_score)
                    category_metrics[category_value]['Mem_helpful_score_norm'].append(helpful_score / 2.0)
            
            # Compute choice accuracy for this question if available
            if qa_id in user_generation:
                gen_result = user_generation[qa_id]
                
                # Check if this is a choice question
                if gen_result.get('choices'):
                    pred = gen_result.get('predicted_choice_id', '').strip()
                    correct = gen_result.get('correct_choice_id', '').strip()
                    
                    # Simple normalization and comparison (same logic as compute_llm_metrics_for_clonemem.py)
                    if pred and correct:
                        is_correct = 1.0 if pred.upper() == correct.upper() else 0.0
                        category_metrics[category_value]['choice_accuracy'].append(is_correct)
    
    # Convert to DataFrame
    rows = []
    for category_value, metrics in category_metrics.items():
        row = {category_key: category_value, 'num_questions': category_qa_counts[category_value]}
        
        # Compute averages for each metric
        for metric_name, values in metrics.items():
            # Remove NaN values
            clean_values = [v for v in values if not (isinstance(v, float) and np.isnan(v))]
            if clean_values:
                row[f'{metric_name}_mean'] = np.mean(clean_values)
                row[f'{metric_name}_std'] = np.std(clean_values)
                row[f'{metric_name}_count'] = len(clean_values)
            else:
                assert metric_name == 'QA_consistency_score'
        
        rows.append(row)
    
    # Create DataFrame and sort by category value
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(by=category_key).reset_index(drop=True)
        
        # Reorder columns: category_key first, num_questions second, then alphabetically
        cols = [category_key, 'num_questions']
        remaining_cols = sorted([c for c in df.columns if c not in cols])
        df = df[cols + remaining_cols]
    
    return df


def main(args):
    print("=" * 60)
    print("Aggregating Metrics by Question Type and Dimension")
    print("=" * 60)

    args.retrieval_dir = f'checkpoints/new_data/{args.method_name}/'
    args.generation_dir = f'checkpoints/new_data/{args.method_name}/generation_results'
    args.llm_metrics_dir = f'checkpoints/new_data/{args.method_name}/generation_results/llm_judge_detailed_results'
    
    # Load QA data
    print(f"\nLoading QA data from: {args.qa_file}")
    user_qa_map, user_info = load_all_qa_data(args.qa_file)
    print(f"Loaded QA data for {len(user_qa_map)} users")
    
    total_qa = sum(len(qa_items) for qa_items in user_qa_map.values())
    print(f"Total QA items: {total_qa}")
    
    # Load retrieval results
    print(f"\nLoading retrieval results from: {args.retrieval_dir}")
    if args.retrieval_pattern:
        print(f"Filtering retrieval files with pattern: '{args.retrieval_pattern}'")
    retrieval_results_map = load_retrieval_results(args.retrieval_dir, args.retrieval_pattern)
    print(f"Loaded retrieval results for {len(retrieval_results_map)} users")
    
    # Load generation results
    print(f"\nLoading generation results from: {args.generation_dir}")
    if args.generation_pattern:
        print(f"Filtering generation files with pattern: '{args.generation_pattern}'")
    generation_results_map = load_generation_results(args.generation_dir, args.generation_pattern)
    print(f"Loaded generation results for {len(generation_results_map)} users")
    
    # Load LLM metrics
    print(f"\nLoading LLM metrics from: {args.llm_metrics_dir}")
    if args.generation_pattern:
        print(f"Filtering LLM metrics files with pattern: '{args.generation_pattern}'")
    llm_metrics_map = load_llm_metrics(args.llm_metrics_dir, args.generation_pattern)
    print(f"Loaded LLM metrics for {len(llm_metrics_map)} users")
    
    # Set output directory
    if not args.out_dir:
        # Use the retrieval directory's parent
        args.out_dir = os.path.join(args.retrieval_dir, 'aggregated_analysis')
    
    os.makedirs(args.out_dir, exist_ok=True)
    print(f"\nOutput directory: {args.out_dir}")
    
    # Aggregate by question_type
    print("\n" + "=" * 60)
    print("Aggregating by Question Type")
    print("=" * 60)
    df_question_type = aggregate_metrics_by_category(
        user_qa_map, retrieval_results_map, generation_results_map, llm_metrics_map, 'question_type'
    )
    
    question_type_file = os.path.join(args.out_dir, 'metrics_by_question_type.csv')
    if not df_question_type.empty:
        df_question_type.to_csv(question_type_file, index=False)
        print(f"\nSaved results to: {question_type_file}")
        print("\nPreview:")
        preview_cols = ['question_type', 'num_questions', 'recall_flat_k10_mean', 
                       'recall_flat_k20_mean', 'QA_consistency_score_mean', 'choice_accuracy_mean']
        available_cols = [c for c in preview_cols if c in df_question_type.columns]
        if available_cols:
            print(df_question_type[available_cols].to_string(index=False))
    else:
        print("No data to save for question_type")
    
    # Aggregate by dimension
    print("\n" + "=" * 60)
    print("Aggregating by Dimension")
    print("=" * 60)
    df_dimension = aggregate_metrics_by_category(
        user_qa_map, retrieval_results_map, generation_results_map, llm_metrics_map, 'dimension'
    )
    
    dimension_file = os.path.join(args.out_dir, 'metrics_by_dimension.csv')
    if not df_dimension.empty:
        df_dimension.to_csv(dimension_file, index=False)
        print(f"\nSaved results to: {dimension_file}")
        print("\nPreview:")
        preview_cols = ['dimension', 'num_questions', 'recall_flat_k10_mean', 
                       'recall_flat_k20_mean', 'QA_consistency_score_mean', 'choice_accuracy_mean']
        available_cols = [c for c in preview_cols if c in df_dimension.columns]
        if available_cols:
            print(df_dimension[available_cols].to_string(index=False))
    else:
        print("No data to save for dimension")
    
    print("\n" + "=" * 60)
    print("Aggregation Complete!")
    print("=" * 60)


if __name__ == "__main__":
    args = parse_args()
    main(args)

