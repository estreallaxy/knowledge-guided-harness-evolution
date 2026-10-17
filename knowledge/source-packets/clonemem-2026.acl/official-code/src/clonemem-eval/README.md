# Evaluate Existing Memory Systems on CloneMem
---
## Overview

The evaluation framework supports four memory systems:
- **Flat Retriever**: Flat embedding-based retrieval with optional expansion methods (similar to LongMemEval)
- **A-Mem**: Agentic memory system with structured memory extraction (summary, keywords, facts) and update capabilities
- **Mem0**: Memory consolidation system with automatic extraction and semantic search
- **Oracle**: Ground truth baseline using known relevant context IDs

## Installation

```bash
# Install basic required dependencies
pip install torch transformers sentence-transformers openai pydantic tqdm backoff rank-bm25 mem0ai qdrant-client

# Set up environment variables
export OPENAI_API_KEY="your-api-key"  # For OpenAI models
export HF_HOME="/path/to/cache"       # Cache directory for HuggingFace models
```

## Supported Embedding Models

All evaluation scripts (except `eval_oracle.py`) support the following embedding models:

- **SentenceTransformer**: `all-MiniLM-L6-v2`, `all-mpnet-base-v2`
- **Contriever**: `contriever` (facebook/contriever)
- **Stella**: `stella` (dunzhang/stella_en_1.5B_v5)
- **GTE**: `gte` (Alibaba-NLP/gte-Qwen2-7B-instruct)
- **OpenAI**: `openai` (text-embedding-3-small)
- **BM25**: `bm25` (sparse retrieval, no embedding)

## Evaluation Scripts

### 1. `eval_amem.py` - A-Mem Evaluation

Evaluates the A-Mem agentic memory system with structured memory extraction and update capabilities.

**Key Features:**
- Extracts structured memories: summary, keywords, and user facts
- Supports memory consolidation and retrieval
- Question decomposition for complex queries
- GPU parallelization across multiple users

**Usage:**

```bash
python eval_amem.py \
    --in_file data/clonemem_benchmark.json \
    --output_dir checkpoints/amem/ \
    --outfile_prefix amem_run \
    --embedding_model stella \
    --llm_model meta-llama/Meta-Llama-3.1-8B-Instruct \
    --backend openai \
    --retrieve_k 20 \
    --num_subquestions 3 \
    --vllm_base_url http://localhost:8001/v1 \
    --device cuda \
    --num_workers 4 \
    --cache_dir /path/to/cache \
    --resume
```

**Arguments:**

**Data & Output:**
- `--in_file`: Path to input JSON file containing user data (default: `data/new_data/all_users_benchmark_en.json`)
- `--output_dir`: Output directory for results (default: `checkpoints/tmp`)
- `--outfile_prefix`: Prefix for output files (default: `default`)

**Model Configuration:**
- `--embedding_model`: Embedding model for retrieval (choices: `all-MiniLM-L6-v2`, `all-mpnet-base-v2`, `contriever`, `stella`, `gte`, `openai`, `bm25`; default: `contriever`)
- `--llm_model`: LLM model for memory extraction and operations (default: `meta-llama/Meta-Llama-3.1-8B-Instruct`)
- `--backend`: LLM backend (choices: `openai`, `ollama`; default: `openai`)
- `--retrieve_k`: Number of memories to retrieve (default: `50`)

**Query Processing:**
- `--num_subquestions`: Number of subquestions to decompose each question into; 0 = no decomposition (default: `0`)

**API Configuration:**
- `--api_key`: API key for LLM backend (default: `EMPTY`)
- `--vllm_base_url`: Base URL for vLLM server if using self-hosted LLM (default: `http://localhost:8001/v1`)

**Hardware & Performance:**
- `--device`: Device for embedding model (e.g., `cuda`, `cuda:0`, `cpu`); auto-detects GPUs if not specified
- `--num_workers`: Number of parallel workers; workers are distributed across GPUs in round-robin fashion (default: `1`)
- `--cache_dir`: Cache directory for models (default: `/data/users1/ywei/data/cache/`)

**Caching & Resume:**
- `--force_reextract`: Force re-extraction of memories even if cache exists (default: `False`)
- `--resume`: Resume from checkpoints and skip already-processed samples (default: `True`)

**Output Format:**

Results are saved as JSON files (one per user) in `{output_dir}/{user_id}_{timestamp}.json`:

```json
{
  "question_id": {
    "question": "What did I post about?",
    "question_time": "2024-03-15",
    "num_contexts_processed": 45,
    "ranked_items": [
      {
        "res_type": "summary",
        "rank": 0,
        "chunk_id": "ctx_123",
        "content": "User posted about...",
        "timestamp": "2024-03-10"
      },
      ...
    ]
  }
}
```

---

### 2. `eval_flat.py` - Flat Retriever Evaluation

Evaluates flat embedding-based retrieval with optional expansion methods. Similar to LongMemEval's approach but adapted for CloneMem.

**Key Features:**
- Flat retrieval without memory consolidation
- Support for multiple expansion methods (summary, keywords, facts)
- Flexible expansion join strategies (none, merge, merge_raw, separate)
- Query decomposition support
- GPU parallelization

**Usage:**

```bash
python eval_flat.py \
    --in_file data/clonemem_benchmark.json \
    --output_dir checkpoints/flat/ \
    --outfile_prefix flat_run \
    --embedding_model stella \
    --index_expansion_method summ,keywords,facts \
    --join_method merge \
    --use_chunk \
    --llm_model meta-llama/Meta-Llama-3.1-8B-Instruct \
    --retrieve_k 20 \
    --num_workers 4
```

**Arguments:**

**Data & Output:**
- `--in_file`: Path to input JSON file (default: `data/new_data/all_users_benchmark_en.json`)
- `--output_dir`: Output directory (default: `checkpoints/new_data/flatten/`)
- `--outfile_prefix`: Output file prefix (default: `default`)

**Expansion Configuration:**
- `--index_expansion_method`: Comma-separated expansion methods (e.g., `summ,keywords,facts`; default: `None`)
  - `summ`: Extract session summaries
  - `keywords`: Extract keyphrases
  - `facts`: Extract user facts
- `--join_method`: How to combine expansions (choices: `none`, `merge`, `merge_raw`, `separate`; default: `none`)
  - `none`: No expansion
  - `merge`: Merge expansions together, keep original content separate
  - `merge_raw`: Merge expansions with original content into single embedding
  - `separate`: Keep expansions separate, retrieve from each independently
- `--use_chunk`: Use original chunk content for retrieval alongside expansions; must be `True` if `merge_raw` (default: `False`)

**Model Configuration:**
- `--embedding_model`: Embedding model (choices: `all-MiniLM-L6-v2`, `all-mpnet-base-v2`, `contriever`, `stella`, `gte`, `openai`, `bm25`; default: `contriever`)
- `--llm_model`: LLM model for query expansion (default: `meta-llama/Meta-Llama-3.1-8B-Instruct`)
- `--backend`: LLM backend (choices: `openai`, `ollama`; default: `openai`)
- `--retrieve_k`: Number of memories to retrieve (default: `50`)

**Query Processing:**
- `--num_subquestions`: Number of subquestions for decomposition; 0 = disabled (default: `0`)

**API Configuration:**
- `--api_key`: API key for LLM backend (default: `''`)
- `--vllm_base_url`: Base URL for vLLM server (default: `http://localhost:8001/v1`)

**Hardware & Performance:**
- `--device`: Device for embedding model (auto-detects GPUs if not specified)
- `--num_workers`: Number of parallel workers; distributed across GPUs (default: `1`)
- `--cache_dir`: Cache directory (default: `/data/users1/ywei/data/cache/`)

**Caching & Resume:**
- `--force_reextract`: Force re-extraction of expansions (default: `False`)
- `--resume`: Resume from checkpoints (default: `True`)

**Expansion Methods Explained:**

This script follows LongMemEval's expansion approach:

1. **No Expansion** (`--join_method none`):
   - Retrieves from original content only

2. **Merge** (`--join_method merge`):
   - Combines all expansions (summary, keywords, facts) into one text per context
   - Creates one embedding for merged expansion + one embedding for original (if `--use_chunk`)

3. **Merge Raw** (`--join_method merge_raw`):
   - Merges expansions AND original content into single text
   - Creates single embedding per context
   - Must set `--use_chunk True`

4. **Separate** (`--join_method separate`):
   - Keeps each expansion type separate
   - Retrieves from each independently and combines scores
   - Optionally includes original content (via `--use_chunk`)

**Output Format:**

Similar to `eval_amem.py`, with additional `res_type` indicating expansion source.

---

### 3. `eval_mem0.py` - Mem0 Evaluation

Evaluates the Mem0 memory system with automatic memory extraction and consolidation.

**Key Features:**
- Automatic structured memory extraction via LLM
- Persistent vector store (Qdrant) for memory storage
- Memory consolidation over time
- Stores both extracted memories and original content

**Important Notes:**
- **No Per-Question Caching**: Unlike A-Mem, Mem0's memory consolidation can update/merge memories over time, making per-question snapshots unreliable
- **Persistent Storage**: Each user gets a separate Qdrant collection at `memories/qdrant_{user_id}_{embedding_model}/`
- **Single Worker Only**: Due to Qdrant limitations, multiprocessing is not currently supported (`--num_workers` must be `1`)

**Usage:**

```bash
python eval_mem0.py \
    --in_file data/clonemem_benchmark.json \
    --output_dir checkpoints/mem0/ \
    --outfile_prefix mem0_run \
    --embedding_model stella \
    --llm_model meta-llama/Meta-Llama-3.1-8B-Instruct \
    --backend vllm \
    --retrieve_k 20 \
    --vllm_base_url http://localhost:8001/v1 \
    --force_reextract \
    --resume
```

**Arguments:**

**Data & Output:**
- `--in_file`: Path to input JSON file (default: `data/new_data/all_users_benchmark_en.json`)
- `--output_dir`: Output directory (default: `checkpoints/new_data/mem0/`)
- `--outfile_prefix`: Output file prefix (default: `default`)

**Model Configuration:**
- `--embedding_model`: Embedding model (choices: `all-MiniLM-L6-v2`, `all-mpnet-base-v2`, `contriever`, `stella`, `gte`, `openai`, `bm25`; default: `contriever`)
- `--llm_model`: LLM model for memory extraction (default: `meta-llama/Meta-Llama-3.1-8B-Instruct`)
- `--backend`: LLM backend (choices: `openai`, `vllm`; default: `vllm`)
- `--retrieve_k`: Number of memories to retrieve (default: `50`)

**API Configuration:**
- `--api_key`: API key for LLM backend (default: `EMPTY`)
- `--vllm_base_url`: Base URL for vLLM server (default: `http://localhost:8001/v1`)
- `--cache_dir`: Cache directory (default: `/data/users1/ywei/data/cache/`)

**Hardware & Performance:**
- `--num_workers`: Number of parallel workers - **MUST BE 1** for Mem0 (default: `1`)

**Caching & Resume:**
- `--force_reextract`: Force re-extraction by clearing vector store (default: `False`)
- `--resume`: Resume from checkpoints and skip processed files (default: `True`)

**Caching Strategy:**

Mem0 uses persistent Qdrant vector storage:
- Each user gets a collection: `memories/qdrant_{user_id}_{embedding_model}/`
- Data persists across runs automatically
- Use `--force_reextract` to clear vector store and re-process
- No per-question memory snapshots (due to consolidation)

**Output Format:**

Results include both extracted memories and original content:

```json
{
  "question_id": {
    "question": "What did I share?",
    "question_time": "2024-03-15",
    "num_contexts_processed": 30,
    "ranked_items": [
      {
        "res_type": "extracted_memory",
        "rank": 0,
        "chunk_id": "ctx_123",
        "content": "Extracted/consolidated memory",
        "timestamp": "2024-03-10",
        "original_content": "Original raw content..."
      },
      ...
    ]
  }
}
```

---

### 4. `eval_oracle.py` - Oracle Baseline

Oracle evaluation using ground truth relevant context IDs. No actual retrieval or embedding is performed.

**Key Features:**
- Uses ground truth `media_ids` from questions
- No retrieval or LLM required
- Provides upper-bound performance baseline
- Fast execution

**Usage:**

```bash
python eval_oracle.py \
    --in_file data/clonemem_benchmark.json \
    --output_dir checkpoints/oracle/ \
    --outfile_prefix oracle_run \
    --num_workers 4 \
    --resume
```

**Arguments:**

**Data & Output:**
- `--in_file`: Path to input JSON file (default: `data/new_data/all_users_benchmark_en.json`)
- `--output_dir`: Output directory (default: `checkpoints/new_data/oracle/`)
- `--outfile_prefix`: Output file prefix (default: `default`)

**Result Configuration:**
- `--use_statement_only`: Use only statement-type evidence as ranked items (default: `False`)
- `--add_statement`: Add statement-type evidence alongside chunk content (default: `False`)

**Performance:**
- `--num_workers`: Number of parallel workers (default: `1`)

**Resume:**
- `--resume`: Resume from checkpoints and skip processed files (default: `False`)

**Output Format:**

```json
{
  "question_id": {
    "question": "What was discussed?",
    "question_time": "2024-03-15",
    "num_contexts_processed": 3,
    "ranked_items": [
      {
        "res_type": "chunk",
        "rank": 0,
        "chunk_id": "ctx_gold_1",
        "content": "Ground truth relevant content",
        "timestamp": "2024-03-10"
      },
      ...
    ]
  }
}
```

---

## Input Data Format

All scripts expect JSON input with the following structure:

```json
{
  "person_name": "user_123",
  "person_id": "user_123",
  "context": [
    {
      "id": "ctx_1",
      "content": "User posted about...",
      "event_date": "2024-03-10"
    },
    ...
  ],
  "qa_items": [
    {
      "id": "q1",
      "question": "What did I post about?",
      "question_time": "2024-03-15",
      "media_ids": ["ctx_1", "ctx_2"],
      "evidence": [
        {
          "statement": "Evidence statement",
          "related_media_id": ["ctx_1"]
        }
      ]
    },
    ...
  ]
}
```

Supports both single user (dict) and multiple users (list of dicts).

## Running with vLLM

To use local LLMs via vLLM:

```bash
# Start vLLM server
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Meta-Llama-3.1-8B-Instruct \
    --port 8001 \
    --tensor-parallel-size 1

# Run evaluation
python eval_amem.py \
    --llm_model meta-llama/Meta-Llama-3.1-8B-Instruct \
    --backend openai \
    --vllm_base_url http://localhost:8001/v1 \
    ...
```


## Evaluation Metrics

Use the `eval/` directory scripts to compute metrics:

```bash
# Compute automatic metrics (recall, precision)
python eval/compute_auto_metrics_for_clonemem.py

# Compute LLM-based metrics (relevance, coherence)
python eval/run_generation.py \
    --in_file=data/clonemem_benchmark.json \
    --retrieval_file="$RETRIEVAL_FILE" \
    --top_k=$K$ \
    --model_name=$MODEL_NAME$ \


python eval/compute_llm_metrics_for_clonemem.py

# Aggregate and visualize
python eval/analysis/aggregate_metrics_by_category.py
python eval/analysis/visualize_all_metrics.py
```

or directly run
```bash
./eval/run_eval.sh
```


## Citation

If you use this code, please cite:

```
[TODO: Add citation once published]
```

## Acknowledgments

This work builds upon:
- **LongMemEval**: Long-term memory evaluation benchmark [link](https://github.com/xiaowu0162/LongMemEval)
- **A-Mem**: Agentic updatable memory system [link](https://github.com/agiresearch/A-mem)
- **Mem0**: Memory consolidation system [link](https://github.com/mem0ai/mem0)