  ---

<div align="center">

# Not All Bits Are Equal: Scale-Dependent Memory Optimization Strategies for Reasoning Models

[![Paper](http://img.shields.io/badge/paper-arxiv.2510.10964-B31B1B.svg)](https://arxiv.org/abs/2510.10964)

</div>

## Description

This repository provides the code for exploring the memory-accuracy trade-offs for reasoning models induced by model size, weight precision, generation length, parallel scaling, and KV cache compression. Below are the key findings from our exploration.

### Key Findings

1. For models effectively smaller than 8-bit 4B, it is more memory-efficient to allocate memory to larger weights than to longer generations, while larger models benefit more from longer generations.

2. 4-bit weights are broadly memory-optimal for knowledge-intensive tasks, while 8-bit or 16-bit weights are more memory-efficient for mathematical reasoning and code generation.

3. Parallel scaling only improves the memory-accuracy trade-off for models effectively larger than 8-bit 4B. The memory-optimal group size increases with the memory budget.

4. Weight quantization alone is not sufficient for memory-optimal reasoning; compressing the KV cache leads to more memory-efficient reasoning.

5. KV cache eviction provides a better memory-accuracy trade-off than KV cache quantization for models with an effective size smaller than an 8-bit 4B model.

## Installation

```bash
# Clone the repository
git clone https://github.com/krafton-ai/not-all-bits-are-equal.git
cd not-all-bits-are-equal

# Create and activate a virtual environment
uv venv
source .venv/bin/activate

# Install the package in editable mode
uv pip install -e .
```

## Model Weight-Only Quantization

Pre-quantized GPTQ checkpoints for Qwen3 models (4-bit and 8-bit) are available on Hugging Face: [huggingface.co/collections/jhyuckkim/qwen3-gptq](https://huggingface.co/collections/jhyuckkim/qwen3-gptq).

To quantize your own models:

```bash
skythought quantize \
  --model Qwen/Qwen3-4B \
  --output-dir ./Qwen3-4B-GPTQ-4b \
  --backend gptq \
  --bits 4
```

## Reproducing Experiments

There are two workflows depending on whether KV cache compression is used:

- **Without KV cache compression** (vLLM backend): `generate` -> `truncate` -> `score`
- **With KV cache compression** (transformers backend): `evaluate` (generates + scores in one shot)

### Workflow A: Without KV cache compression

This workflow uses the fast vLLM backend and applies budget forcing in two stages:

1. **Generate**: Produce full-length reasoning traces for every problem. `--min-tokens` forces the model to generate up to the maximum token budget via "Wait" continuation tokens, ensuring each trace is long enough to be truncated to any target budget.
2. **Truncate**: Cut each trace at each target budget (e.g., 2000, 6000, ..., 30000 tokens), then append an answer-forcing separator (`**Final Answer**\n\\boxed{`) and generate a few more tokens so the model produces a final answer at each budget.
3. **Score**: Evaluate correctness of the truncated answers.

#### 1. Generate full-length traces

```bash
skythought generate \
  --model jhyuckkim/Qwen3-8B-GPTQ-8b \
  --task aime25_1 \
  --backend vllm \
  --backend-args tensor_parallel_size=1 \
  --sampling-params temperature=0.6 \
  --n 32 \
  --min-tokens 32000 \
  --result-dir results/
```

#### 2. Truncate and answer-force at each budget

```bash
skythought truncate \
  --run-dir results/<run_dir> \
  --budgets 2000,6000,10000,14000,18000,22000,26000,30000 \
  --separator "**Final Answer**\\n\\\\boxed{" \
  --max-new-tokens 10 \
  --batch-size 32
```

This creates `truncate_2000/`, `truncate_6000/`, ..., `truncate_30000/` subdirectories inside `<run_dir>`.

#### 3. Score results

```bash
skythought score \
  --task aime25_1 \
  --run-dir results/<run_dir>/truncate_10000
```

### Workflow B: With KV cache compression

KV cache compression runs through the Hugging Face `transformers` backend, which handles budget forcing internally. The `evaluate` command generates and scores in a single pass. Budget targets are specified via the `budgets` list in `--sampling-params`.

**KV cache quantization (HQQ):**

```bash
skythought evaluate \
  --model jhyuckkim/Qwen3-8B-GPTQ-8b \
  --task aime25_1 \
  --backend transformers \
  --backend-args "torch_dtype=bfloat16" \
  --sampling-params '{"temperature":0.6, "budgets":[2000,6000,10000,14000,18000,22000,26000,30000], "cache_implementation":"quantized", "cache_config":{"nbits":4, "backend":"HQQ", "axis_key":1, "axis_value":1, "device":"cuda", "residual_length":128, "compute_dtype":"bfloat16"}}' \
  --n 32 \
  --batch-size 1 \
  --result-dir results/
```

**KV cache eviction (R-KV):**

```bash
skythought evaluate \
  --model jhyuckkim/Qwen3-8B-GPTQ-8b \
  --task aime25_1 \
  --backend transformers \
  --backend-args "torch_dtype=bfloat16" \
  --sampling-params '{"temperature":0.6, "budgets":[2000,6000,10000,14000,18000,22000,26000,30000], "cache_implementation":"rkv", "cache_config":{"budget":8192}}' \
  --n 32 \
  --batch-size 1 \
  --result-dir results/
```

**KV cache eviction (StreamingLLM):**

```bash
skythought evaluate \
  --model jhyuckkim/Qwen3-8B-GPTQ-8b \
  --task aime25_1 \
  --backend transformers \
  --backend-args "torch_dtype=bfloat16" \
  --sampling-params '{"temperature":0.6, "budgets":[2000,6000,10000,14000,18000,22000,26000,30000], "cache_implementation":"streamingllm", "cache_config":{"window_size":4096, "max_capacity_prompt":8192}}' \
  --n 32 \
  --batch-size 1 \
  --result-dir results/
```

The `evaluate` command scores automatically. To re-score or score individual budgets separately:

```bash
skythought score \
  --task aime25_1 \
  --run-dir results/<run_dir>/truncate_10000
```

### Parallel Scaling Evaluation

Parallel scaling evaluation reuses the same generated traces but selects answers differently: majority voting picks the most common answer among a group, while PRM best-of-N uses a process reward model to select the highest-scoring trace.

#### Majority Voting

```bash
skythought score-majority \
  --task aime25_1 \
  --run-dir results/<run_dir>/truncate_10000 \
  --group-size 8 \
  --num-trials 32
```

#### PRM Best-of-N Scoring

```bash
python score_prm_bestof.py \
  --run-dir results/<run_dir>/truncate_10000 \
  --group-size 8 \
  --num-trials 32 \
  --prm-model-id sail/ActPRM-X \
  --write-scores-cache
```

### Post-Processing

#### Collect and Aggregate Results

```bash
python collect_results.py \
  --input_folders results/ \
  --output_file results_summary.csv
```

#### Calculate Memory Usage

```bash
python calculate_memory.py \
  --input-csv results_summary.csv \
  --config-json memory_config.json
```

## Citation

```bibtex
@article{kim2025not,
  title={Not All Bits Are Equal: Scale-Dependent Memory Optimization Strategies for Reasoning Models},
  author={Kim, Junhyuck and Ewer, Ethan and Moon, Taehong and Park, Jongho and Papailiopoulos, Dimitris},
  journal={arXiv preprint arXiv:2510.10964},
  year={2025}
}
```

## Acknowledgements

This codebase is built on [SkyThought](https://github.com/NovaSky-AI/SkyThought) by the NovaSky team. The KV cache eviction implementation references [R-KV](https://github.com/Zefan-Cai/R-KV).
