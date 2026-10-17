#!/usr/bin/env python3
"""
Mem0 Evaluation Script

This script benchmarks the Mem0 memory system on a custom dataset with temporal awareness.
The process involves:
1. Sorting contexts and questions by timestamp
2. For each question, only adding memories from contexts that occurred BEFORE the question time
3. Retrieving relevant memories based on questions
4. Saving results in a structured format

Mem0 automatically extracts and stores structured memories from the raw context,
and provides semantic search capabilities.

Note: Unlike A-Mem, we don't cache per-question memory snapshots because Mem0's memory
consolidation can update/merge memories over time, making snapshots unreliable.

**Storing Original Content alongside Extracted Memories:**
By default, mem0 only stores the extracted/structured memories. To also preserve
the original content (like A-Mem does), we store the original content in the 
'metadata' field when adding memories. During retrieval, we can then access both:
- The extracted/structured memory (mem0's LLM-processed version)
- The original raw content (stored in metadata['original_content'])
- The original context ID (stored in metadata['context_id'])

This allows us to generate results similar to A-Mem with both 'original' and 
'extracted_memory' result types.

**Caching Strategy:**
Mem0 uses persistent storage (Qdrant vector store) that automatically saves data
to disk. Our caching strategy:

1. Vector Store Persistence:
   - Each user gets a separate Qdrant collection at: 
     memories/qdrant_{user_id}_{embedding_model}/
   - Data persists across runs automatically
   - Memories are incrementally added as questions are processed

2. No Per-Question Caching:
   - Unlike A-Mem, we don't snapshot memory state per question
   - Mem0's memory consolidation can update/merge memories over time
   - Caching would be unreliable and potentially incorrect
   - Each run processes all questions from scratch

3. Cache Validation:
   - Uses --force_reextract to force re-processing (clears vector store)
   - Use --resume to skip already-processed result files

Usage:
    python eval_mem0.py --in_file data/sample.json \
                        --output_dir checkpoints/mem0/ \
                        --embedding_model contriever \
                        --llm_model meta-llama/Meta-Llama-3.1-8B-Instruct \
                        --retrieve_k 20

Supported embedding models:
- SentenceTransformer: all-MiniLM-L6-v2, all-mpnet-base-v2
- Contriever: facebook/contriever
- Stella: dunzhang/stella_en_1.5B_v5
- GTE: Alibaba-NLP/gte-Qwen2-7B-instruct
"""

import os
import re
import time
import json
import random
import traceback
from datetime import datetime
import argparse
import multiprocessing as mp
from rank_bm25 import BM25Okapi

from tqdm import tqdm
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed
)
from mem0_utils import Memory

# Model name mapping
MODEL_CONFIG = {
    'all-MiniLM-L6-v2': {'model_name': 'all-MiniLM-L6-v2', 'model_type': 'sentence-transformer'},
    'all-mpnet-base-v2': {'model_name': 'all-mpnet-base-v2', 'model_type': 'sentence-transformer'},
    'contriever': {'model_name': 'facebook/contriever', 'model_type': 'contriever'},
    'stella': {'model_name': 'dunzhang_stella_en_1.5B_v5', 'model_type': 'stella'},
    'gte': {'model_name': 'Alibaba-NLP/gte-Qwen2-7B-instruct', 'model_type': 'gte'},
    'bm25': {'model_name': 'bm25', 'model_type': 'bm25'},  # BM25 model (no embedding)
    'openai': {'model_name': 'text-embedding-3-small', 'model_type': 'openai'}  # OpenAI embedding
}


TEMPLATE_MEM0 = """Memories for user {user_id}:

    {memories}
"""

RETRY_TIMES = 10
WAIT_TIME = 5


@retry(
    retry=retry_if_exception_type(Exception),
    wait=wait_fixed(WAIT_TIME),
    stop=stop_after_attempt(RETRY_TIMES),
    reraise=True
)
def add_memory(client, user_id, message, timestamp, context_id=None, metadata=None):
    """
    Add memory to mem0 with optional metadata to preserve original content.
    
    Note: Mem0 uses SQLite for history storage which can encounter lock errors
    when processing memories in quick succession. The retry decorator helps
    handle transient "database is locked" errors.
    
    Args:
        client: Mem0 Memory client
        user_id: User identifier
        message: Message content (can be string or list of message dicts)
        timestamp: Timestamp for the memory
        context_id: Original context ID to store in metadata
        metadata: Additional metadata dict to store with the memory
    """
    start = time.time()

    # Prepare metadata to store original content and context ID
    mem_metadata = metadata or {}
    if context_id:
        mem_metadata['context_id'] = context_id
    
    # Store original message content in metadata
    if isinstance(message, str):
        mem_metadata['original_content'] = message
    elif isinstance(message, list):
        # For conversation format, store the full conversation
        mem_metadata['original_messages'] = json.dumps(message)

    result = client.add(
        message,
        user_id=user_id,
        metadata=mem_metadata
    )
    duration_ms = (time.time() - start) * 1000

    return result, duration_ms


@retry(
    retry=retry_if_exception_type(Exception),
    wait=wait_fixed(WAIT_TIME),
    stop=stop_after_attempt(RETRY_TIMES),
    reraise=True
)
def search_memory(
    client, 
    query, 
    user_id, 
    top_k=20
):
    """
    Search memories and return results with both extracted and original content.
    
    The search results will include:
    - memory: The extracted/structured memory by mem0's LLM
    - metadata: Contains original_content (raw input) and context_id
    """
    start = time.time()

    results = client.search(
        query=query,
        user_id=user_id,
    )

    memories = [
        {
            "memory": memory["memory"],  # Extracted/structured memory
            "timestamp": memory.get("created_at", ""),
            "score": round(memory["score"], 2),
            "id": memory["id"],
            "metadata": memory["metadata"],  # Contains original_content and context_id
        }
        for memory in results["results"]
    ]

    memories_formatted = [
        f"{item['timestamp']}: {item['memory']}" for item in memories
    ]

    context = TEMPLATE_MEM0.format(
        user_id=user_id,
        memories=json.dumps(memories_formatted, indent=4)
    )

    duration_ms = (time.time() - start) * 1000

    return context, memories, duration_ms


def verify_memories_exist(client, user_id, expected_count=None):
    """Verify that memories exist in the vector store"""
    try:
        # Try to get all memories for this user
        all_memories = client.get_all(user_id=user_id)
        
        if isinstance(all_memories, dict):
            actual_count = len(all_memories.get('results', []))
        elif isinstance(all_memories, list):
            actual_count = len(all_memories)
        else:
            actual_count = 0
        
        if expected_count is not None:
            if actual_count >= expected_count:
                return True, actual_count
            else:
                print(f"⚠️  Expected {expected_count} memories, found {actual_count}")
                return False, actual_count
        else:
            return True, actual_count
            
    except Exception as e:
        raise Exception(f"⚠️  Failed to verify memories: {str(e)}")


def process_user(user_data, top_k, save_path, args):
    """
    Process a single user's data with temporal awareness: for each question, only retrieve from 
    contexts that occurred before the question time.
    
    Uses post-retrieval filtering to ensure temporal correctness since Mem0's persistent
    vector store contains all memories and cannot be easily snapshotted per question.
    """
    user_name = user_data["person_name"]
    user_id = user_data["person_id"]
    
    print(f"\n{'='*60}")
    print(f"Processing user: {user_name} ({user_id})")
    print(f"Context items: {len(user_data.get('context', []))}")
    print(f"QA items: {len(user_data.get('qa_items', []))}")
    print(f"{'='*60}\n")
    
    # Generate cache identifiers
    llm_model_name = args.llm_model.replace('/', '_')
    embedding_model_name = args.embedding_model
    
    # Setup vector store path (persistent storage for Mem0)
    vector_store_path = os.path.join(args.memories_dir, f"qdrant_{user_id}_{embedding_model_name}")
    
    config = {
        'llm': {
            'provider': args.backend,
            'config': {
                'model': args.llm_model,
                'temperature': 0.7,
                'max_tokens': 5000,
                'api_key': args.api_key,
            }
        },
        'embedder': {
            'provider': 'huggingface',
            'config': {
                'model': MODEL_CONFIG[args.embedding_model]['model_name'],
            }
        },
        'vector_store': {
            'provider': 'qdrant',
            'config': {
                'path': vector_store_path,  # Persistent storage path
                'collection_name': f"mem0_{user_id}",
                # TODO use this as text embedding model has dimension other than 1536, may need manual adjustment
                "embedding_model_dims": 768,
                "host": "localhost",
            }
        }
    }
    assert args.embedding_model in ['contriever', 'openai'], "Only 'contriever' and 'openai' embedding models are supported in Mem0 for now."
    if args.embedding_model == 'openai':
        config['embedder']['provider'] = 'openai'
        config['embedder']['config']['model'] = MODEL_CONFIG[args.embedding_model]['model_name']
        config['embedder']['config']['api_key'] = args.api_key
        config['vector_store']['config']['embedding_model_dims'] = 1536  # OpenAI embedding dimension
    if args.vllm_base_url:
        config['llm']['config']['vllm_base_url'] = args.vllm_base_url

    client = Memory.from_config(config)

    # Sort contexts by event_date for temporal processing
    contexts = sorted(user_data['context'], key=lambda x: datetime.fromisoformat(x["event_date"]))
    
    # Sort questions by question_time
    qa_items = sorted(user_data['qa_items'], key=lambda x: datetime.fromisoformat(x['question_time']))
    
    print(f"🔍 Processing {len(contexts)} context items and {len(qa_items)} questions with temporal awareness...")
    
    # Track which contexts have been added and corpus IDs for mapping
    added_context_ids = set()
    added_memory_ids = {}
    context_pointer = 0  # Points to the next context to add
    
    results = {}
    
    # Process each question in temporal order
    for question_dict in tqdm(qa_items, desc=f"Processing questions for {user_name}"):
        question_id = question_dict['id']
        question = question_dict['question']
        question_time_str = question_dict['question_time']
        question_time = datetime.fromisoformat(question_time_str)
        
        # Add all contexts that occurred before this question and haven't been added yet
        contexts_added_count = 0
        failed_contexts = []
        
        while context_pointer < len(contexts):
            ctx = contexts[context_pointer]
            ctx_time = datetime.fromisoformat(ctx["event_date"])
            
            # Stop if this context is after the question time
            if ctx_time > question_time:
                break
            
            context_id = ctx['id']
            
            # Skip if already added
            if context_id in added_context_ids:
                context_pointer += 1
                continue
            
            timestamp = datetime.fromisoformat(ctx["event_date"])
            
            try:
                # Add memory with timestamp and metadata containing original content
                result, duration_ms = add_memory(
                    client=client,
                    user_id=user_id,
                    message=ctx['content'],
                    timestamp=timestamp,
                    context_id=context_id,
                    metadata={'event_date': ctx['event_date']}
                )
                
                # Store memory ID mapping (result contains memory IDs)
                mem_ids = [r.get('id') for r in result['results'] if 'id' in r]
                if mem_ids:
                    added_memory_ids[context_id] = mem_ids
                    contexts_added_count += 1
                else:
                    failed_contexts.append((context_id, "No memory IDs returned"))
                    print(f"⚠️  Warning: No memory IDs returned for context {context_id} thus no valid memories are extracted")
                    
                
                added_context_ids.add(context_id)
                
            except Exception as e:
                failed_contexts.append((context_id, str(e)))
                # raise Exception(f"⚠️  Error adding memory {context_id}: {str(e)}")
                # TODO
                print(f"⚠️  Error adding memory {context_id}: {str(e)}. THIS SHOULD ONLY HAPPEN for user 沈临川")
            
            context_pointer += 1
        
        if contexts_added_count > 0:
            print(f"  Question {question_id}: Added {contexts_added_count} new contexts (total: {len(added_context_ids)})")
        
        if failed_contexts:
            print(f"  ⚠️  Failed to add {len(failed_contexts)} contexts for this question")
        
        # Perform retrieval for this question (only from memories added before question time)
        try:
            # Search memories - this searches ALL memories in the vector store
            context, memories, duration_ms = search_memory(
                client=client,
                query=question,
                user_id=user_id,
                top_k=top_k * 2  # Get more results to account for filtering
            )
            
            # CRITICAL: Filter memories to only include those from contexts that existed at the time of this question (temporal awareness)
            valid_context_ids = added_context_ids.copy()
            filtered_memories = []
            for memory_dict in memories:
                metadata = memory_dict['metadata']
                context_id = metadata.get('context_id')
                
                # Only include memories from contexts that existed before this question
                if context_id in valid_context_ids:
                    filtered_memories.append(memory_dict)
                    
                # Stop once we have enough results
                if len(filtered_memories) >= top_k:
                    break
            
            # Format results in the expected format (similar to A-Mem)
            ranked_items = []
            for rank, memory_dict in enumerate(filtered_memories):
                metadata = memory_dict['metadata']
                original_content = metadata.get('original_content', '') or metadata.get('original_messages', '')
                context_id = metadata['context_id']
                
                # Add original content (like A-Mem's 'original' res_type)
                if original_content:
                    ranked_items.append({
                        'res_type': 'chunk',
                        'rank': rank,
                        'mem0_id': memory_dict['id'],
                        'chunk_id': context_id,
                        'content': original_content,
                        'timestamp': memory_dict.get('timestamp', ''),
                        'score': memory_dict['score']
                    })
                
                # Add extracted memory (like A-Mem's 'extract_context' res_type)
                ranked_items.append({
                    'res_type': 'extracted_memory',
                    'rank': rank,
                    'mem0_id': memory_dict['id'],
                    'chunk_id': context_id,
                    'content': memory_dict['memory'],
                    'timestamp': memory_dict.get('timestamp', ''),
                    'score': memory_dict['score']
                })
            
            results[question_id] = {
                'question': question,
                'question_time': question_time_str,
                'num_contexts_processed': len(added_context_ids),
                'ranked_items': ranked_items,
                'retrieval_time_ms': duration_ms
            }
            
        except Exception as e:
            print(f"⚠️  Error searching for question {question_id}: {str(e)}")
            traceback.print_exc()
            results[question_id] = {
                'question': question,
                'question_time': question_time_str,
                'num_contexts_processed': len(added_context_ids),
                'ranked_items': [],
                'error': str(e)
            }
    
    # Save results
    output_data = {
        'person_id': user_id,
        'person_name': user_name,
        'results': results,
        'total_contexts': len(contexts),
        'total_questions': len(qa_items),
        'status': 'completed'
    }
    
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Saved results for {user_name} to {save_path}")
    print(f"📊 Final statistics: {len(added_context_ids)} contexts processed, {len(results)} questions answered")
    
    return output_data


def process_user_wrapper(user_data_with_args):
    """
    Wrapper function for multiprocessing.
    Unpacks user_data and args, then calls process_user.
    """

    user_data, args, output_dir, timestamp = user_data_with_args
    user_name = user_data.get('person_name', 'unknown')
    user_id = user_data.get('person_id', 'unknown')
    
    # Generate output filename (no timestamp in filename like eval_amem.py)
    output_filename = f"{args.outfile_prefix}_{user_id}_{args.embedding_model}.json"
    save_path = os.path.join(output_dir, output_filename)
    
    # Check if already processed (resume functionality)
    if args.resume and os.path.exists(save_path):
        print(f"⏭️  Skipping {user_name} - already processed at {save_path}")
        with open(save_path, 'r', encoding='utf-8') as f:
            user_results = json.load(f)
        return (user_id, user_results, save_path, None)
    
    print(f"\n{'='*60}")
    print(f"Processing user: {user_name} ({user_id})")
    print(f"Context items: {len(user_data.get('context', []))}")
    print(f"QA items: {len(user_data.get('qa_items', []))}")
    print(f"{'='*60}\n")
    
    try:
        user_results = process_user(user_data, args.retrieve_k, save_path, args)
        return (user_id, user_results, save_path, None)
    except Exception as e:
        error_msg = f"❌ Error processing {user_name}: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        return (user_id, None, save_path, error_msg)


def main(args):
    """Main function to run the mem0 evaluation"""
    frame = "mem0"
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)
    
    # Create memories directory for caching
    args.memories_dir = os.path.join(output_dir, 'memories')
    os.makedirs(args.memories_dir, exist_ok=True)
    
    # Load input data
    print(f"Loading data from {args.in_file}...")
    try:
        with open(args.in_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        # Try loading as JSONL
        with open(args.in_file, 'r', encoding='utf-8') as f:
            data = [json.loads(line) for line in f]
    
    # Determine if data is single user or list of users
    if isinstance(data, dict) and 'person_name' in data:
        # Single user format
        users_data = [data]
    elif isinstance(data, list):
        # Multiple users format
        users_data = data
    else:
        raise ValueError("Input data format not recognized. Expected single user dict or list of users.")
    
    print(f"Found {len(users_data)} user(s) to process")
    
    # Generate a single timestamp for all users to maintain consistency
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    start_time = time.time()
    
    # Process each user
    all_results = {}
    
    if args.num_workers > 1:
        # Multiprocessing mode
        print(f"\n🚀 Using multiprocessing with {args.num_workers} workers")
        
        # Prepare arguments for each user
        user_args = [
            (user_data, args, output_dir, timestamp)
            for user_data in users_data
        ]
        
        # Process users in parallel
        with mp.Pool(processes=args.num_workers) as pool:
            results_list = pool.map(process_user_wrapper, user_args)
        
        # Collect results
        for user_id, user_results, save_path, error_msg in results_list:
            if user_results is not None:
                all_results[user_id] = user_results
            if error_msg:
                print(error_msg)
    else:
        # Sequential processing (original behavior)
        for user_data in users_data:
            user_id, user_results, save_path, error_msg = process_user_wrapper(
                (user_data, args, output_dir, timestamp)
            )
            if user_results is not None:
                all_results[user_id] = user_results
            if error_msg:
                print(error_msg)
    
    elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"✅ All done in {elapsed:.2f}s")
    print(f"Processed {len(all_results)} user(s)")
    print(f"Results saved to: {output_dir}")
    print(f"{'='*60}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mem0 Retrieval Evaluation")
    parser.add_argument('--in_file', type=str, default='data/new_data/all_users_benchmark_en.json', help='Input JSON file')
    parser.add_argument('--output_dir', type=str, default='checkpoints/new_data/mem0/', help='Output directory')
    parser.add_argument('--outfile_prefix', type=str, default='default', help='Output file prefix')

    parser.add_argument('--embedding_model', type=str, default='contriever',
                       choices=['all-MiniLM-L6-v2', 'all-mpnet-base-v2', 'contriever', 'stella', 'gte', 'openai', 'bm25'],
                       help='Embedding model for retrieval')
    parser.add_argument('--llm_model', type=str, default='meta-llama/Meta-Llama-3.1-8B-Instruct', help='LLM model for memory extraction')
    parser.add_argument('--backend', type=str, default='vllm', choices=['openai', 'vllm'], help='LLM backend')
    parser.add_argument('--retrieve_k', type=int, default=50, help='Number of memories to retrieve')

    parser.add_argument('--api_key', type=str, default='EMPTY', help='API key for LLM backend (if needed)')
    parser.add_argument('--vllm_base_url', type=str, default='http://localhost:8001/v1', help='Base URL for vLLM server (if using self-hosted)')
    parser.add_argument('--cache_dir', type=str, default='/data/users1/ywei/data/cache/', help='Cache directory for models')
    
    # Hardware configuration
    parser.add_argument('--num_workers', type=int, default=1, help='Number of parallel workers for processing multiple users (default: 1, no multiprocessing)')
    
    # Cache configuration
    parser.add_argument('--force_reextract', action='store_true', help='Force re-extraction of memories even if cache exists', default=False)
    
    # Resume configuration
    parser.add_argument('--resume', action='store_true', help='Resume from checkpoints and skip already-processed samples', default=True)
    
    args = parser.parse_args()
    if args.vllm_base_url == 'none' or args.backend == 'openai':
        args.vllm_base_url = None

    # TODO
    assert args.num_workers == 1, "Mem0 has some problem with qdrant vector store thus does not support multiprocessing for now, please set --num_workers 1"
    
    print(f"Configuration:")
    print(f"  Embedding model: {args.embedding_model}")
    print(f"  LLM model: {args.llm_model}")
    print(f"  Retrieve K: {args.retrieve_k}")
    print(f"  Backend: {args.backend}")
    print(f"  Output dir: {args.output_dir}")
    print(f"  Number of workers: {args.num_workers}")
    
    main(args)