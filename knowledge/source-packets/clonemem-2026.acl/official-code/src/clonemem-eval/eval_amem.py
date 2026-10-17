#!/usr/bin/env python3
"""
Supported embedding models:
- SentenceTransformer: all-MiniLM-L6-v2, all-mpnet-base-v2, etc.
- Contriever: facebook/contriever
- Stella: dunzhang/stella_en_1.5B_v5
- GTE: Alibaba-NLP/gte-Qwen2-7B-instruct

"""

import sys
import os
import json
import json_repair
import time
from tqdm import tqdm
import pickle
import argparse
from datetime import datetime
import multiprocessing as mp
from functools import partial
import torch
from pydantic import BaseModel, Field
from typing import List
import backoff
import openai
from openai import OpenAI

from amem_utils import FlexibleAgenticMemorySystem
from llm_controller import LLMController


@backoff.on_exception(backoff.constant, (openai.RateLimitError), 
                      interval=5)
def chat_completions_with_backoff(client, **kwargs):
    return client.chat.completions.create(**kwargs)


class QueryResponse(BaseModel):
    keywords: str = Field(..., description="Generated keywords for the query")


class SubQuestions(BaseModel):
    """Pydantic model for structured output of question decomposition."""
    subquestions: List[str] = Field(..., description="List of decomposed subquestions")

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


class FlexibleAmemRetriever:
    """A-mem retriever with flexible embedding model support"""
    
    def __init__(self, 
                 embedding_model='all-MiniLM-L6-v2',
                 llm_model='gpt-4o-mini', 
                 backend='openai', 
                 retrieve_k=10,
                 device=None,
                 cache_dir=None,
                 api_key=None,
                 vllm_base_url=None):
        
        # Get model config
        if embedding_model in MODEL_CONFIG:
            model_config = MODEL_CONFIG[embedding_model]
        else:
            # Assume it's a sentence-transformer model
            model_config = {'model_name': embedding_model, 'model_type': 'sentence-transformer'}
        
        # Initialize flexible memory system
        self.memory_system = FlexibleAgenticMemorySystem(
            model_name=model_config['model_name'],
            model_type=model_config['model_type'],
            llm_backend=backend,
            llm_model=llm_model,
            device=device,
            cache_dir=cache_dir,
            api_key=api_key,
            base_url=vllm_base_url
        )
        self.retriever_llm = LLMController(backend=backend, model=llm_model, api_key=api_key, base_url=vllm_base_url)
        self.retrieve_k = retrieve_k if retrieve_k > 0 else 100000  # get all memories
        
        self.llm_model = llm_model
        self.client = OpenAI(
            api_key=api_key if 'gpt' in llm_model else 'EMPTY',
            base_url=None if 'gpt' in llm_model else vllm_base_url,
        )
        
        # Track corpus IDs for mapping retrieved memories back
        self.corpus_ids = []
        self.corpus_content = []
        self.corpus_timestamps = []

    def _decompose_question(self, question, num_subquestions=3):
        """
        Decompose a question into multiple subquestions using LLM.
        
        Args:
            question: The original question to decompose
            num_subquestions: Number of subquestions to generate
            
        Returns:
            List of subquestions
        """
        decomposition_prompt = f"""Given the following question, decompose it into maximum {num_subquestions} more specific subquestions that would help answer the original question. Each subquestion should focus on a different aspect or detail of the original question.

Original Question: {question}

Generate up to {num_subquestions} subquestions that are:
1. More specific and focused than the original
2. Cover different aspects of the original question
3. Can be answered independently

Provide the subquestions as a list."""

        kwargs = {
            'model': self.llm_model,
            'messages': [
                {"role": "user", "content": decomposition_prompt}
            ],
            'n': 1,
            'temperature': 0.7,  # Slightly higher temperature for more diverse subquestions
            'max_tokens': 500
        }
        
        if 'gpt' in self.llm_model:
            kwargs['response_format'] = SubQuestions
            completion = self.client.chat.completions.parse(**kwargs)
        else:
            kwargs['extra_body'] = {'guided_json': SubQuestions.model_json_schema()}
            completion = self.client.chat.completions.create(**kwargs)

        subquestions_text = completion.choices[0].message.content
        subquestions_text = json_repair.loads(subquestions_text)
        
        parsed_response = SubQuestions(**subquestions_text)
        if parsed_response is not None and parsed_response.subquestions:
            return parsed_response.subquestions[:num_subquestions]
        
        # Fallback: return original question if decomposition fails
        return [question]
    
    def add_memory(self, content, time_stamp=None, corpus_id=None, keywords=None, context=None, tags=None):
        """Add memory and track its corpus ID with retry logic
        
        Args:
            content: The content of the memory
            time_stamp: Timestamp of the memory
            corpus_id: Original corpus ID for tracking
            keywords: Pre-extracted keywords (if cached, skips LLM extraction)
            context: Pre-extracted context (if cached, skips LLM extraction)
            tags: Pre-extracted tags (if cached, skips LLM extraction)
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Pass cached metadata to skip LLM extraction if available
                note_id, new_note = self.memory_system.add_note(
                    content, 
                    time=time_stamp, 
                    raw_sess_id=corpus_id,
                    keywords=keywords,
                    context=context,
                    tags=tags
                )
                self.corpus_ids.append(corpus_id)
                self.corpus_content.append(content)
                self.corpus_timestamps.append(time_stamp)
                return note_id, new_note  # Return the note ID for tracking
            except json.JSONDecodeError as e:
                print(f"⚠️  JSON decode error on attempt {attempt + 1}/{max_retries}: {str(e)}")
                print(f"   Content preview: {content[:100]}...")
                if attempt < max_retries - 1:
                    print(f"   Retrying...")
                    time.sleep(1)  # Brief pause before retry
                else:
                    print(f"   ❌ Failed after {max_retries} attempts, skipping this memory")
                    raise
            except Exception as e:
                print(f"⚠️  Error adding memory: {str(e)}")
                raise
    

    def retrieve(self, question):
        """
        Retrieve using A-mem's method and return in LongMemEval format
        Returns: (indices, corpus_ids)
        """
        # NOTE: here we manually consolidate memory for retrieval but origianl A-mem does not do this
        self.memory_system.consolidate_memories()
        
        # Retrieve using A-mem's retrieval system (get indices directly)
        # find_related_memories returns (memory_str, indices)
        _, memory_indices = self.memory_system.find_related_memories(question, k=self.retrieve_k)
        
        
        return memory_indices


def load_per_context_cache(context_id, per_context_cache_dir):
    """Load cached metadata for a specific context item"""
    cache_file = os.path.join(per_context_cache_dir, f"{context_id}.json")
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Failed to load per-context cache for {context_id}: {str(e)}")
    return None


def save_per_context_cache(context_id, metadata, per_context_cache_dir):
    """Save metadata for a specific context item"""
    os.makedirs(per_context_cache_dir, exist_ok=True)
    cache_file = os.path.join(per_context_cache_dir, f"{context_id}.json")
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️  Failed to save per-context cache for {context_id}: {str(e)}")


def process_user(user_data, save_path, args, device=None):
    """
    Process user data with temporal awareness: for each question, only retrieve from 
    contexts that occurred before the question time.
    
    Uses two-tier caching:
    1. Per-context cache: Stores extracted metadata (keywords, context, tags) for each context item
    2. Per-question final cache: Stores complete memory system state at the time of each question
    """
    user_name = user_data["person_name"]
    user_id = user_data["person_id"]
    sessions = user_data["context"]

    # Use provided device or auto-detect
    if device is None:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'

    # Generate cache paths
    # NOTE: Different LLM models will extract different metadata, so cache separately
    llm_model_name = args.llm_model.replace('/', '_')  # Replace / in model names for filename
    
    # Per-context cache directory (individual metadata for each context)
    per_context_cache_dir = os.path.join(args.memories_dir, f"{user_id}_{llm_model_name}_per_context")
    
    # Per-question final cache directory (complete memory system at time of each question)
    per_question_cache_dir = os.path.join(args.memories_dir, f"{user_id}_{llm_model_name}_per_question")
    
    os.makedirs(args.memories_dir, exist_ok=True)
    os.makedirs(per_question_cache_dir, exist_ok=True)

    # Initialize retriever
    retriever = FlexibleAmemRetriever(
            embedding_model=args.embedding_model,
            llm_model=args.llm_model,
            backend=args.backend,
            retrieve_k=args.retrieve_k,
            device=device,
            cache_dir=args.cache_dir,
            api_key=args.api_key,
            vllm_base_url=args.vllm_base_url
        )

    # Sort contexts by event_date for temporal processing
    contexts = sorted(user_data['context'], key=lambda x: datetime.fromisoformat(x["event_date"]))
    
    # Sort questions by question_time
    qa_items = sorted(user_data['qa_items'], key=lambda x: datetime.fromisoformat(x['question_time']))
    
    print(f"🔍 Processing {len(contexts)} context items and {len(qa_items)} questions with temporal awareness...")
    
    # Check if per-context cache is available
    per_context_cache_available = os.path.exists(per_context_cache_dir)
    if per_context_cache_available:
        cached_count = len([f for f in os.listdir(per_context_cache_dir) if f.endswith('.json')])
        print(f"Found per-context cache directory with {cached_count} cached items")
    
    # Track which contexts have been added
    added_context_ids = set()
    context_pointer = 0  # Points to the next context to add
    
    results = {}
    
    # Process each question in temporal order
    for question_dict in tqdm(qa_items, desc=f"Processing questions for {user_name}"):
        question_id = question_dict['id']
        question = question_dict['question']
        question_time_str = question_dict['question_time']
        question_time = datetime.fromisoformat(question_time_str)
        
        # Check if per-question cache exists
        question_cache_file = os.path.join(per_question_cache_dir, f"{question_id}_memories.pkl")
        
        if os.path.exists(question_cache_file) and not args.force_reextract:
            # Load cached memory state for this question
            with open(question_cache_file, 'rb') as f:
                cached_memories = pickle.load(f)
            retriever.memory_system.memories = cached_memories
            retriever.memory_system.consolidate_memories()
            
            # Update context pointer to skip already processed contexts
            for ctx in contexts:
                ctx_time = datetime.fromisoformat(ctx["event_date"])
                if ctx_time <= question_time and ctx['id'] not in added_context_ids:
                    added_context_ids.add(ctx['id'])
                    context_pointer += 1
            print(f"  Loaded cached memories for question {question_id}, skipping context addition")
        
        # Add all contexts that occurred before this question and haven't been added yet
        cache_hits = 0
        cache_misses = 0
        
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
            
            timestamp = str(ctx_time)
            
            # Try to load per-context cache
            cached_metadata = load_per_context_cache(context_id, per_context_cache_dir)
            
            if cached_metadata is not None and not args.force_reextract:
                # Use cached metadata - pass to add_memory to skip LLM extraction
                retriever.add_memory(
                    content=ctx['content'],
                    time_stamp=timestamp,
                    corpus_id=context_id,
                    keywords=cached_metadata['keywords'],
                    context=cached_metadata['context'],
                    tags=cached_metadata['tags']
                )
                cache_hits += 1
            else:
                # No cache available, extract metadata using LLM
                _, new_note = retriever.add_memory(
                    content=ctx['content'],
                    time_stamp=timestamp,
                    corpus_id=context_id
                )
                
                # Save per-context cache for future use
                metadata_to_cache = {
                    'keywords': new_note.keywords,
                    'context': new_note.context,
                    'tags': new_note.tags
                }
                save_per_context_cache(context_id, metadata_to_cache, per_context_cache_dir)
                cache_misses += 1
            
            added_context_ids.add(context_id)
            context_pointer += 1
        
        if cache_hits > 0 or cache_misses > 0:
            print(f"  Question {question_id}: Added {cache_hits + cache_misses} contexts ({cache_hits} cached, {cache_misses} new)")
        
        # Save per-question memory state (for caching)
        if not os.path.exists(question_cache_file) or args.force_reextract:
            with open(question_cache_file, 'wb') as f:
                pickle.dump(retriever.memory_system.memories, f)
        
        # Handle question decomposition if enabled
        if args.num_subquestions > 0:
            # Decompose question into subquestions
            try:
                subquestions = retriever._decompose_question(question, num_subquestions=args.num_subquestions)
                print(f"  Decomposed into {len(subquestions)} subquestions")
            except Exception as e:
                print(f"⚠️  Failed to decompose question {question_id}: {str(e)}")
                subquestions = [question]  # Fallback to original question
        else:
            # No decomposition, use original question
            subquestions = [question]
        
        # Perform retrieval for each subquestion
        all_ranked_items = []
        for subq_idx, subquestion in enumerate(subquestions):
            memory_indices = retriever.retrieve(subquestion)

            # A-Mem stores memories in a dict, need to convert indices to memory IDs
            memory_ids = list(retriever.memory_system.memories.keys())
            
            # Build ranked items for this subquestion
            for rank, idx in enumerate(memory_indices):
                if idx >= len(memory_ids):
                    print(f"⚠️  Warning: Index {idx} out of range for {len(memory_ids)} memories (question {question_id})")
                    continue
                
                mem_id = memory_ids[idx]
                mem = retriever.memory_system.memories[mem_id]
                corpus_id = mem.raw_sess_id
                raw_content = mem.content  # Use content as raw_content
                
                # Verify we have the original corpus ID for tracking
                if corpus_id is None:
                    raise Exception(f"⚠️  Warning: Memory at index {idx} (mem_id={mem_id}) has no raw_sess_id")
                
                ranked_item = {
                    'res_type': 'chunk', 
                    'rank': rank, 
                    'chunk_id': corpus_id, 
                    'content': raw_content, 
                    'timestamp': mem.timestamp,
                    'subquestion': subquestion,
                    'subquestion_id': subq_idx
                }
                all_ranked_items.append(ranked_item)
                
                context_item = {
                    'res_type': 'extract_context', 
                    'rank': rank, 
                    'chunk_id': corpus_id, 
                    'content': mem.context, 
                    'timestamp': mem.timestamp,
                    'subquestion': subquestion,
                    'subquestion_id': subq_idx
                }
                all_ranked_items.append(context_item)
                
                keywords_item = {
                    'res_type': 'extract_keywords', 
                    'rank': rank, 
                    'chunk_id': corpus_id, 
                    'content': ', '.join(mem.keywords), 
                    'timestamp': mem.timestamp,
                    'subquestion': subquestion,
                    'subquestion_id': subq_idx
                }
                all_ranked_items.append(keywords_item)
                
                tags_item = {
                    'res_type': 'extract_tags', 
                    'rank': rank, 
                    'chunk_id': corpus_id, 
                    'content': ', '.join(mem.tags), 
                    'timestamp': mem.timestamp,
                    'subquestion': subquestion,
                    'subquestion_id': subq_idx
                }
                all_ranked_items.append(tags_item)

        results[question_id] = {
            'question': question, 
            'question_time': question_time_str,
            'num_contexts_processed': len(added_context_ids),
            'subquestions': subquestions if args.num_subquestions > 0 else None,
            'ranked_items': all_ranked_items
        }

    # Save results
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Saved results for {user_name} to {save_path}")
    print(f"📊 Final statistics: {len(added_context_ids)} contexts processed, {len(results)} questions answered")
    return results


def process_user_wrapper(user_data_with_args):
    """
    Wrapper function for multiprocessing.
    Unpacks user_data and args, then calls process_user.
    Supports GPU assignment for parallel processing.
    """
    user_data, args, gpu_id, output_dir, timestamp = user_data_with_args
    user_name = user_data.get('person_name', 'unknown')
    user_id = user_data.get('person_id', 'unknown')
    
    # Set device based on GPU ID
    if gpu_id is not None and gpu_id >= 0:
        device = f'cuda:{gpu_id}'
        print(f"🎯 Process assigned to GPU {gpu_id} for user {user_name}")
    else:
        device = 'cpu'
        print(f"🎯 Process assigned to CPU for user {user_name}")
    
    # Generate output filename
    subq_suffix = f"_subq{args.num_subquestions}" if args.num_subquestions > 0 else ""
    output_filename = f"{args.outfile_prefix}_{user_id}_{args.embedding_model}{subq_suffix}.json"
    save_path = os.path.join(output_dir, output_filename)
    
    # Check if already processed (resume functionality)
    if args.resume and os.path.exists(save_path):
        print(f"⏭️  Skipping {user_name} - already processed at {save_path}")
        with open(save_path, 'r', encoding='utf-8') as f:
            user_results = json.load(f)
        return (user_id, user_results, save_path, None)
    
    print(f"\n{'='*60}")
    print(f"Processing user: {user_name} ({user_id}) on {device}")
    print(f"Context items: {len(user_data.get('context', []))}")
    print(f"QA items: {len(user_data.get('qa_items', []))}")
    print(f"{'='*60}\n")
    
    try:
        user_results = process_user(user_data, save_path, args, device=device)
        return (user_id, user_results, save_path, None)
    except Exception as e:
        error_msg = f"❌ Error processing {user_name} on {device}: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        return (user_id, None, save_path, error_msg)


if __name__ == "__main__":
    # Set multiprocessing start method to 'spawn' for CUDA compatibility
    # This must be done before any CUDA operations
    mp.set_start_method('spawn', force=True)
    
    parser = argparse.ArgumentParser(description="A-mem Retrieval Stage with Flexible Model Support (Stage 1)")
    parser.add_argument('--in_file', type=str, default='data/new_data/all_users_benchmark_en.json', help='Input JSON file')
    parser.add_argument('--output_dir', type=str, default='checkpoints/tmp', help='Output directory')
    parser.add_argument('--outfile_prefix', type=str, default='default', help='Output file prefix')
    
    # Model configuration
    parser.add_argument('--embedding_model', type=str, default='contriever',
                       choices=['all-MiniLM-L6-v2', 'all-mpnet-base-v2', 'contriever', 'stella', 'gte', 'openai', 'bm25'],
                       help='Embedding model for retrieval')
    parser.add_argument('--llm_model', type=str, default='meta-llama/Meta-Llama-3.1-8B-Instruct', help='LLM model for query expansion')
    parser.add_argument('--backend', type=str, default='openai', choices=['openai', 'ollama'], help='LLM backend')
    parser.add_argument('--retrieve_k', type=int, default=50, help='Number of memories to retrieve')

    # Question decomposition
    parser.add_argument('--num_subquestions', type=int, default=0, help='Number of subquestions to decompose each question into (0 = no decomposition)')

    parser.add_argument('--api_key', type=str, default='EMPTY', help='API key for LLM backend (if needed)')
    parser.add_argument('--vllm_base_url', type=str, default='http://localhost:8001/v1', help='Base URL for vLLM server (if using self-hosted)')
    
    # Hardware configuration
    parser.add_argument('--device', type=str, default=None, help='Device for embedding model (e.g., cuda, cuda:0, cpu). If not specified, auto-detects GPUs')
    parser.add_argument('--num_workers', type=int, default=1, help='Number of parallel workers. With GPUs, workers are distributed across available GPUs in round-robin fashion (default: 1)')
    parser.add_argument('--cache_dir', type=str, default='/data/users1/ywei/data/cache/', help='Cache directory for models')
    
    # Cache configuration
    parser.add_argument('--force_reextract', action='store_true', help='Force re-extraction of memories even if cache exists', default=False)
    
    # Resume configuration
    parser.add_argument('--resume', action='store_true', help='Resume from checkpoints and skip already-processed samples', default=True)
    
    args = parser.parse_args()

    if args.vllm_base_url == 'none' or 'gpt' in args.llm_model.lower():
        args.vllm_base_url = None
    
    # Load input data
    print(f"Loading data from {args.in_file}...")
    with open(args.in_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
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
    
    # Create output directory
    output_dir = args.output_dir
    args.memories_dir = os.path.join(output_dir, 'memories')
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(args.memories_dir, exist_ok=True)
    
    # Determine device(s) and GPU availability
    num_gpus = torch.cuda.device_count() if torch.cuda.is_available() else 0
    
    if args.device:
        # User specified device explicitly
        device_mode = args.device
        use_gpus = args.device.startswith('cuda')
        print(f"Using user-specified device: {device_mode}")
    elif num_gpus > 0:
        # GPUs available - use them
        device_mode = 'cuda'
        use_gpus = True
        print(f"🎮 Detected {num_gpus} GPU(s)")
    else:
        # No GPUs available - use CPU
        device_mode = 'cpu'
        use_gpus = False
        print(f"No GPUs detected, using CPU")
    
    # Determine number of workers
    if args.num_workers > 1:
        if use_gpus and num_gpus > 0:
            # Limit workers to number of GPUs if not specified
            max_workers = min(args.num_workers, num_gpus)
            if args.num_workers > num_gpus:
                print(f"⚠️  Requested {args.num_workers} workers but only {num_gpus} GPU(s) available.")
                print(f"   Setting workers to {max_workers} to match GPU count.")
            num_workers = max_workers
        else:
            num_workers = args.num_workers
    else:
        num_workers = 1
    
    print(f"Embedding model: {args.embedding_model}")
    print(f"LLM model: {args.llm_model}")
    print(f"Number of subquestions: {args.num_subquestions if args.num_subquestions > 0 else 'disabled (no decomposition)'}")
    print(f"Number of workers: {num_workers}")
    
    # Generate a single timestamp for all users to maintain consistency
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Process each user
    all_results = {}
    
    if num_workers > 1:
        # Multiprocessing mode with GPU assignment
        print(f"\n🚀 Using multiprocessing with {num_workers} workers")
        
        if use_gpus and num_gpus > 0:
            # Assign users to GPUs in round-robin fashion
            print(f"📍 Distributing {len(users_data)} users across {num_gpus} GPU(s)")
            user_args = []
            for idx, user_data in enumerate(users_data):
                gpu_id = idx % num_gpus  # Round-robin assignment
                user_args.append((user_data, args, gpu_id, output_dir, timestamp))
            
            # Show GPU assignment distribution
            gpu_counts = {}
            for _, _, gpu_id, _, _ in user_args:
                gpu_counts[gpu_id] = gpu_counts.get(gpu_id, 0) + 1
            print(f"   GPU assignment distribution: {gpu_counts}")
        else:
            # CPU-only mode
            print(f"📍 Processing on CPU")
            user_args = [
                (user_data, args, -1, output_dir, timestamp)  # -1 indicates CPU
                for user_data in users_data
            ]
        
        # Process users in parallel
        with mp.Pool(processes=num_workers) as pool:
            results_list = pool.map(process_user_wrapper, user_args)
        
        # Collect results
        for user_id, user_results, save_path, error_msg in results_list:
            if user_results is not None:
                all_results[user_id] = user_results
            if error_msg:
                print(error_msg)
    else:
        # Sequential processing (original behavior)
        print(f"\n📝 Sequential processing (single worker)")
        gpu_id = 0 if use_gpus and num_gpus > 0 else -1
        
        for user_data in users_data:
            user_id, user_results, save_path, error_msg = process_user_wrapper(
                (user_data, args, gpu_id, output_dir, timestamp)
            )
            if user_results is not None:
                all_results[user_id] = user_results
            if error_msg:
                print(error_msg)
    
    print(f"\n{'='*60}")
    print(f"✓ Processing complete!")
    print(f"Processed {len(all_results)} user(s)")
    print(f"Results saved to: {output_dir}")
    print(f"{'='*60}")
