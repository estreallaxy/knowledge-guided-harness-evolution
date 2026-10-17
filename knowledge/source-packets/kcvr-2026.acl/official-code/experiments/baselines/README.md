# Baseline Implementations

This directory contains implementations of baseline methods reported in Table 1 of the paper.

## Baselines

### 1. GPT-4o (Zero-Shot)

- **Type**: Zero-shot, API-based
- **Script**: `gpt4o_zero_shot.py`
- **Requirements**: OpenAI API key
- **Note**: Requires API access, results may vary with API version

### 2. InternVL-Chat (Zero-Shot)

- **Type**: Zero-shot, local model
- **Script**: `internvl_zero_shot.py`
- **Requirements**: InternVL3-8B base model
- **Note**: Uses base model without fine-tuning

### 3. InternVL-SFT (No Planning)

- **Type**: Fine-tuned, no knowledge planning
- **Script**: `internvl_sft_no_planning.py`
- **Requirements**: Trained model without planning components
- **Note**: Same training setup as full model, but prompt excludes plan

### 4. VideoLLaMA2-SFT

- **Type**: Fine-tuned alternative architecture
- **Script**: `videollama2_sft.py`
- **Requirements**: VideoLLaMA2-7B model
- **Note**: Requires separate model download

### 5. Text-RAG Baseline

- **Type**: Static knowledge retrieval
- **Script**: `text_rag_baseline.py`
- **Requirements**: Same as InternVL-SFT
- **Note**: Used in ablation studies (B2)

## Running Baselines

### Option 1: Run All Baselines

```bash
bash experiments/baselines/run_all_baselines.sh
```

### Option 2: Run Individual Baselines

```bash
# GPT-4o (requires API key)
export OPENAI_API_KEY="your-api-key"
python src/baselines/gpt4o_zero_shot.py \
    --dataset data/splits/v2_7subj_trainvaltest.json \
    --split test \
    --output-dir experiments/paper_results/baselines/gpt4o

# InternVL Zero-Shot
python src/baselines/internvl_zero_shot.py \
    --model-path models/base/InternVL3-8B \
    --dataset data/splits/v2_7subj_trainvaltest.json \
    --split test \
    --output-dir experiments/paper_results/baselines/internvl_zero_shot

# InternVL-SFT (No Planning)
python src/baselines/internvl_sft_no_planning.py \
    --model-path models/checkpoints/internvl_sft_no_planning \
    --dataset data/splits/v2_7subj_trainvaltest.json \
    --split test \
    --output-dir experiments/paper_results/baselines/internvl_sft_no_planning
```

## Expected Results

See Table 1 in the paper for expected metric values. Key comparisons:

- **GPT-4o**: Strong zero-shot performance, but lower KPC/LOC
- **InternVL-Chat**: Baseline VLM performance
- **InternVL-SFT (No Planning)**: Shows improvement from fine-tuning, but lacks structure
- **Full Model**: Best performance across all metrics

## Notes

- Some baselines (GPT-4o) require external API access
- Baseline models need to be trained separately (see `EXPERIMENTS.md`)
- Results are saved to `experiments/paper_results/baselines/`

