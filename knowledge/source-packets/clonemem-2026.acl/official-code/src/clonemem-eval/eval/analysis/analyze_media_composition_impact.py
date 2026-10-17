import json
import argparse
import os
import sys
from datetime import datetime
from collections import Counter
from tqdm import tqdm

# Add project root to Python path
PROJECT_ROOT = os.path.expanduser("~/playground/AgentMem/clonemem_adaptation")
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def parse_args():
    parser = argparse.ArgumentParser(description="Analyze impact of media composition on LLM metrics")
    parser.add_argument('--qa_file', type=str, 
                        default='data/new_data/all_users_benchmark_en.json',
                        help='Input file containing all users QA items and context')
    parser.add_argument('--llm_metrics_dir', type=str,
                        default='checkpoints/new_data/amem/generation_results/llm_judge_detailed_results',
                        help='Directory containing LLM judge metrics files')
    parser.add_argument('--out_file', type=str, default=None,
                        help='Output JSON file to save analysis results')
    return parser.parse_args()


def extract_user_id_from_filename(filename):
    """Extract user_id from llm metric filename."""
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
    
    return None


def load_all_qa_data(qa_file):
    """
    Load all users' QA data and context.
    Returns: 
        - user_data_map: {user_id: user_data_dict}
    """
    with open(qa_file, 'r') as f:
        all_users_data = json.load(f)
    
    user_data_map = {}
    
    for user_data in all_users_data:
        user_id = user_data['person_id']
        user_data_map[user_id] = user_data
    
    return user_data_map


def load_llm_metrics(llm_dir):
    """
    Load all LLM judge metrics files.
    Returns: {user_id: llm_metrics_dict}
    """
    llm_metrics = {}
    
    if not os.path.exists(llm_dir):
        print(f"Warning: LLM metrics directory not found: {llm_dir}")
        return llm_metrics
    
    for filename in os.listdir(llm_dir):
        if 'llm_judge' in filename:
            filepath = os.path.join(llm_dir, filename)
            user_id = extract_user_id_from_filename(filename)
            
            if user_id:
                with open(filepath, 'r') as f:
                    llm_metrics[user_id] = json.load(f)
    
    return llm_metrics


def get_contexts_before_question(contexts, question_time):
    """
    Filter contexts that occurred before the question time (temporal awareness).
    
    Args:
        contexts: List of context items with 'event_date' and 'medium' fields
        question_time: datetime object or ISO string of question time
    
    Returns:
        List of context items that occurred before the question
    """
    if isinstance(question_time, str):
        question_time = datetime.fromisoformat(question_time)
    
    valid_contexts = []
    for ctx in contexts:
        ctx_time = datetime.fromisoformat(ctx['event_date'])
        if ctx_time <= question_time:
            valid_contexts.append(ctx)
    
    return valid_contexts


def compute_media_composition(contexts):
    """
    Compute media type composition from a list of contexts.
    
    Args:
        contexts: List of context items with 'medium' field
    
    Returns:
        dict with:
            - 'counts': {media_type: count}
            - 'percentages': {media_type: percentage}
            - 'total': total number of contexts
    """
    if not contexts:
        return {
            'counts': {},
            'percentages': {},
            'total': 0
        }
    
    # Count media types
    media_counter = Counter(ctx['medium'] for ctx in contexts)
    total = len(contexts)
    
    # Compute percentages
    percentages = {media_type: (count / total) * 100 
                   for media_type, count in media_counter.items()}
    
    return {
        'counts': dict(media_counter),
        'percentages': percentages,
        'total': total
    }


def analyze_media_impact(user_data_map, llm_metrics_map):
    """
    Analyze the impact of media composition on LLM metrics for each question.
    
    Returns:
        List of dicts, each containing:
            - question_id
            - user_id
            - person_name
            - question_type
            - dimension
            - question_time
            - num_contexts_before_question
            - media_composition_counts
            - media_composition_percentages
            - LLM metrics (QA_consistency_score, Mem_recall, Mem_helpful_score, etc.)
    """
    results = []
    
    print(f"Analyzing media composition impact for {len(user_data_map)} users...")
    
    for user_id, user_data in tqdm(user_data_map.items(), desc="Processing users"):
        person_name = user_data['person_name']
        contexts = user_data['context']
        qa_items = user_data['qa_items']
        
        # Get LLM metrics for this user
        user_llm_metrics = llm_metrics_map[user_id]
        detailed_llm_results = user_llm_metrics['detailed_llm_results']
        
        if not detailed_llm_results:
            print(f"  ⚠️  No LLM metrics found for user {person_name} ({user_id})")
            continue
        
        # Process each QA item
        for qa_item in qa_items:
            question_id = qa_item['id']
            question_type = qa_item['question_type']
            dimension = qa_item['dimension']
            question_time = qa_item['question_time']
            
            # Check if we have LLM metrics for this question
            if question_id not in detailed_llm_results:
                continue
            
            llm_metrics = detailed_llm_results[question_id]
            
            # Get contexts that occurred before this question (temporal awareness)
            contexts_before = get_contexts_before_question(contexts, question_time)
            
            # Compute media composition
            composition = compute_media_composition(contexts_before)
            
            # Build result record
            result = {
                'question_id': question_id,
                'user_id': user_id,
                'person_name': person_name,
                'question_type': question_type,
                'dimension': dimension,
                'question_time': question_time,
                'num_contexts_before_question': composition['total'],
                'media_composition_counts': composition['counts'],
                'media_composition_percentages': composition['percentages'],
                # LLM metrics
                'QA_consistency_score': llm_metrics['QA_consistency_score'],
                'Mem_recall': llm_metrics['Mem_recall'],
                'Mem_helpful_score': llm_metrics['Mem_helpful_score'],
                'QA_consistency_reason': llm_metrics['QA_consistency_reason'],
                'Mem_helpful_reason': llm_metrics['Mem_helpful_reason'],
                'Mem_hits': llm_metrics['Mem_hits'],
            }
            
            results.append(result)
    
    return results


def main(args):
    print("=" * 60)
    print("Analyzing Media Composition Impact on LLM Metrics")
    print("=" * 60)
    
    # Load QA data with context
    print(f"\nLoading QA data from: {args.qa_file}")
    user_data_map = load_all_qa_data(args.qa_file)
    print(f"Loaded data for {len(user_data_map)} users")
    
    total_qa = sum(len(user_data['qa_items']) for user_data in user_data_map.values())
    print(f"Total QA items: {total_qa}")
    
    # Load LLM metrics
    print(f"\nLoading LLM metrics from: {args.llm_metrics_dir}")
    llm_metrics_map = load_llm_metrics(args.llm_metrics_dir)
    print(f"Loaded LLM metrics for {len(llm_metrics_map)} users")
    
    # Analyze media composition impact
    print("\n" + "=" * 60)
    print("Computing media composition for each question...")
    print("=" * 60)
    
    results = analyze_media_impact(user_data_map, llm_metrics_map)
    
    print(f"\nProcessed {len(results)} questions with LLM metrics")
    
    # Set output file
    if not args.out_file:
        llm_dir_parent = os.path.dirname(args.llm_metrics_dir)
        output_dir = os.path.join(llm_dir_parent, 'media_composition_analysis')
        os.makedirs(output_dir, exist_ok=True)
        args.out_file = os.path.join(output_dir, 'media_composition_impact_per_question.json')
    
    # Save results
    with open(args.out_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Results saved to: {args.out_file}")
    
    # Print summary statistics
    print("\n" + "=" * 60)
    print("Summary Statistics")
    print("=" * 60)
    
    # Collect all unique media types
    all_media_types = set()
    for result in results:
        all_media_types.update(result['media_composition_counts'].keys())
    
    print(f"\nUnique media types found: {len(all_media_types)}")
    print(f"Media types: {sorted(all_media_types)}")
    
    # Show distribution of context counts
    context_counts = [r['num_contexts_before_question'] for r in results]
    if context_counts:
        print(f"\nContext count statistics:")
        print(f"  Min contexts: {min(context_counts)}")
        print(f"  Max contexts: {max(context_counts)}")
        print(f"  Avg contexts: {sum(context_counts) / len(context_counts):.2f}")
    
    # Show sample results
    print(f"\nSample result (first question):")
    if results:
        sample = results[0]
        print(f"  Question ID: {sample['question_id']}")
        print(f"  Person: {sample['person_name']}")
        print(f"  Question type: {sample['question_type']}")
        print(f"  Dimension: {sample['dimension']}")
        print(f"  Contexts before question: {sample['num_contexts_before_question']}")
        print(f"  Media composition (counts): {sample['media_composition_counts']}")
        print(f"  Media composition (percentages): {sample['media_composition_percentages']}")
        print(f"  QA consistency score: {sample['QA_consistency_score']}")
        print(f"  Mem recall: {sample['Mem_recall']}")
        print(f"  Mem helpful score: {sample['Mem_helpful_score']}")
    
    print("\n" + "=" * 60)
    print("Analysis Complete!")
    print("=" * 60)


if __name__ == "__main__":
    args = parse_args()
    main(args)
