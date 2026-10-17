# ANCHOR: Calibrated Probabilities from LLM Outputs

ANCHOR is a three-stage framework that transforms raw LLM outputs into well-calibrated probabilities.

> [中文版文档](README_zh.md)

## Table of Contents

- [Project Structure](#project-structure)
- [Environment Setup](#environment-setup)
- [Configuration](#configuration)
- [Datasets](#datasets)
- [Pipeline](#pipeline)
  - [Stage 1: Factor-Space Construction](#stage-1-factor-space-construction)
  - [Stage 2: Context-Aware Mapping](#stage-2-context-aware-mapping)
  - [Stage 3: Probabilistic Inference](#stage-3-probabilistic-inference)
  - [Evaluation](#evaluation)
- [FactCheck Pipeline (XSum)](#factcheck-pipeline-xsum)
- [Baseline Methods](#baseline-methods)
- [FAQ](#faq)

---

## Project Structure

```
ANCHOR/
├── README.md
├── README_zh.md
├── requirements.txt
├── data/                          # Dataset directory
│   ├── common2sense.json          # Primary dataset
│   ├── common2sense_human_annotation.csv   # Human annotations (for evaluation)
│   ├── common2sense_human_annotation.json
│   ├── xsum.json                  # FactCheck dataset
│   ├── plasma.json / today.json / cnn.json / covid.json / expertqa.json
│   └── ...
└── code/
    ├── utils/
    │   ├── config.py              # <-- Global config (API key, model path, etc.)
    │   ├── utils.py               # LLM call wrapper
    │   ├── prompt_shots.py        # Prompt templates (common2sense)
    │   ├── prompt_shots_fact_check.py  # Prompt templates (FactCheck)
    │   └── response_parse_utils.py    # Response parsing utilities
    ├── run/
    │   ├── iterative_factor_gen.py              # Stage 1
    │   ├── hierarchical_condition_mapping.py    # Stage 2
    │   ├── casual_bayesian_train.py             # Stage 3
    │   ├── evaluate_nb_cbn.py                   # Evaluation script
    │   ├── compute_nb_cbn.py                    # F1 score computation
    │   ├── iterative_factor_gen_fact_check.py   # Stage 1 (FactCheck)
    │   ├── hierarchical_condition_mapping_fact_check.py  # Stage 2 (FactCheck)
    │   ├── scenario_analysis.py / scenario_inference.py / scenario_train.py  # BIRD baseline
    │   └── results/               # Output directory (auto-created)
    ├── baselines/                 # Baseline methods
    └── evaluation/                # BIRD evaluation scripts
```

---

## Environment Setup

### 1. Create Conda Environment

```bash
conda create -n anchor python=3.10 -y
conda activate anchor
```

### 2. Install Dependencies

```bash
cd ANCHOR
pip install -r requirements.txt
```

> **Note:**
> - `requirements.txt` includes all necessary dependencies (`httpx`, `nltk`, `sentence-transformers>=5.0.0`, etc.).
> - If you only use a remote API (e.g., gpt-4o-mini), `vllm` is not required. For local model deployment, install it separately: `pip install vllm==0.6.3`.

### 3. Download Embedding Model

Stage 1 and Stage 2 require the `all-MiniLM-L6-v2` sentence embedding model for factor clustering and KNN retrieval.

```bash
# Option A: Download via Python
python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
model.save('/your/local/path/all-MiniLM-L6-v2')
print('Model saved successfully.')
"

# Option B: Download via huggingface-cli
pip install huggingface_hub
huggingface-cli download sentence-transformers/all-MiniLM-L6-v2 --local-dir /your/local/path/all-MiniLM-L6-v2
```

After downloading, set the path in `code/utils/config.py` under `MiniLM_L6_PATH`.

---

## Configuration

Edit `code/utils/config.py` before running:

```python
# Local path to the embedding model
MiniLM_L6_PATH = '/your/local/path/all-MiniLM-L6-v2'

# Dataset: common2sense, plasma, today, cnn, xsum, covid, expertqa
dataset_name = "common2sense"

# Data and output directories (relative to code/run/)
dataset_file_dic = "../../data/"
save_file_dic = "./results/"

# LLM API configuration (OpenAI-compatible endpoint)
model_name = 'gpt-4o-mini'
base_url = 'https://your-api-endpoint/v1'
api_key = 'your-api-key-here'
```

> **Tip:** Any OpenAI-compatible API endpoint is supported, including OpenAI official, Azure OpenAI, local vLLM services, etc.

---

## Datasets

| Dataset | Filename | Description |
|---------|----------|-------------|
| Common2Sense | `common2sense.json` | Commonsense reasoning scenarios (primary, 216 items) |
| XSum | `xsum.json` | Fact-checking scenarios (FactCheck) |
| PLASMA | `plasma.json` | Commonsense reasoning scenarios |
| Today | `today.json` | Commonsense reasoning scenarios |
| CNN | `cnn.json` | News scenarios |
| COVID | `covid.json` | COVID-related scenarios |
| ExpertQA | `expertqa.json` | Expert Q&A scenarios |

---

## Pipeline

> **Important:** The three stages **must be executed sequentially**, as each stage's output is the next stage's input.
>
> **Working directory:** All commands are run from the `code/run/` directory.
>
> **PYTHONPATH:** Must be set to the `code/` directory for proper `utils` module imports.

```bash
# Enter the run directory
cd ANCHOR/code/run

# Ensure the output directory exists
mkdir -p results
```

### Stage 1: Factor-Space Construction

Iteratively generates factors via reverse abduction, then applies UMAP + HDBSCAN for hierarchical clustering.

```bash
PYTHONPATH=.. python iterative_factor_gen.py \
    --start 0 \
    --end 5 \
    --cluster
```

**Arguments:**

| Argument | Default | Description |
|----------|---------|-------------|
| `--start` | 0 | Starting data index |
| `--end` | 1000 | Ending data index (set to 5 for quick testing) |
| `--target` | 40 | Target number of factors per scenario |
| `--batch` | 5 | Batch size per generation round |
| `--rounds` | 10 | Maximum iteration rounds |
| `--cluster` | off | Enable clustering pruning (recommended) |
| `--model_name` | from config | LLM model name |
| `--dataset_name` | from config | Dataset name |

**Output file:**
```
results/{dataset}_{model}_{start}_{end}_factors.json
```

**Note:** Subsequent stages look for `{dataset}_{model}_0_1000_factors_processed_lowercased.json` by default. If your `--end` is not 1000, create a symlink:

```bash
# Example: if --end 5
cd results
ln -sf {dataset}_{model}_0_5_factors.json {dataset}_{model}_0_1000_factors_processed_lowercased.json
cd ..
```

---

### Stage 2: Context-Aware Mapping

Uses hierarchical KNN retrieval to match relevant factors from the factor library for each condition, filtered by LLM voting and self-reflection.

```bash
PYTHONPATH=.. python hierarchical_condition_mapping.py \
    --start 0 \
    --end 5 \
    --K1 3 \
    --K2 5 \
    --num_prompts 3 \
    --enable_self_reflection \
    --max_retries 5
```

**Arguments:**

| Argument | Default | Description |
|----------|---------|-------------|
| `--start` | 0 | Starting data index |
| `--end` | 1000 | Ending data index |
| `--K1` | 3 | Number of top clusters to retrieve |
| `--K2` | 5 | Number of top factors per cluster |
| `--num_prompts` | 3 | Number of LLM voting rounds |
| `--vote_ratio` | 0.5 | Voting threshold ratio |
| `--alpha` | 0.5 | Weight for cluster name vs. factor content |
| `--max_retries` | 5 | Max retries for LLM response parsing |
| `--enable_self_reflection` | on | Enable self-reflection step |
| `--disable_self_reflection` | - | Disable self-reflection step |

**Input file:**
```
results/{dataset}_{model}_0_1000_factors_processed_lowercased.json   # Stage 1 output
```

**Output file:**
```
results/{dataset}_{model}_{start}_{end}_condition_mapping.json
```

**Note:** Stage 3 looks for `{dataset}_{model}_0_1000_condition_mapping.json` by default. Create a symlink if needed:

```bash
cd results
ln -sf {dataset}_{model}_0_5_condition_mapping.json {dataset}_{model}_0_1000_condition_mapping.json
cd ..
```

---

### Stage 3: Probabilistic Inference

Constructs Naive Bayes (NB) and Causal Bayesian Networks (CBN), uses LLM to identify latent variables and initialize parameters, then computes calibrated probabilities.

```bash
PYTHONPATH=.. python casual_bayesian_train.py \
    --start 0 \
    --end 5 \
    --max_retries 5
```

**Arguments:**

| Argument | Default | Description |
|----------|---------|-------------|
| `--start` | 0 | Starting data index |
| `--end` | 1000 | Ending data index |
| `--max_retries` | 20 | Max retries for LLM response parsing |
| `--mapping_type` | `pruned_cluster` | Mapping type (`pruned_cluster` / `init_cluster` / `uncluster`) |
| `--use_cot` | `_cot_v1_` | CoT prompt variant |
| `--factor_prob_type` | `llm_` | Factor probability source |
| `--latent_prob_type` | `llm` | Latent variable probability source |
| `--SMOOTH_ALPHA` | 0.5 | Smoothing parameter |
| `--ablation` | `false` | Ablation experiment mode (off by default) |

**Input file:**
```
results/{dataset}_{model}_0_1000_condition_mapping.json   # Stage 2 output
```

**Output file:**
```
results/{dataset}_{model}_{model}_bn_compare_add_both{use_cot}{factor_prob_type}{latent_prob_type}_{mapping_type}.json
```

Example: `common2sense_gpt-4o-mini_gpt-4o-mini_bn_compare_add_both_cot_v1_llm_llm_pruned_cluster.json`

---

### Evaluation

Evaluation requires human annotation data (`data/common2sense_human_annotation.csv` and `data/common2sense_human_annotation.json`).

> **Note:** `evaluate_nb_cbn.py` contains a hardcoded path `common2sense_qwen2.5-2b_0_1000_factors.json`. If you use a different model, you need to modify this path or create a corresponding symlink.

```bash
# Step 1: Run evaluation script (generate comparison results)
PYTHONPATH=.. python evaluate_nb_cbn.py \
    --start 0 \
    --end 5

# Step 2: Compute F1 scores
# You need to modify the `filename` variable in compute_nb_cbn.py to point to Step 1's output file
PYTHONPATH=.. python compute_nb_cbn.py
```

---

## FactCheck Pipeline (XSum)

FactCheck datasets like XSum use dedicated scripts. The workflow is similar to the main pipeline:

```bash
# Stage 1: Factor generation
PYTHONPATH=.. python iterative_factor_gen_fact_check.py \
    --dataset_name xsum \
    --start 0 \
    --end 5 \
    --cluster

# Create symlink (if needed)
cd results
ln -sf xsum_gpt-4o-mini_0_5_factors.json xsum_gpt-4o-mini_0_1000_factors.json
cd ..

# Stage 2: Condition mapping
PYTHONPATH=.. python hierarchical_condition_mapping_fact_check.py \
    --dataset_name xsum \
    --start 0 \
    --end 5 \
    --enable_self_reflection \
    --max_retries 5

# Stage 3: Use the main script (set dataset_name to xsum in config.py)
PYTHONPATH=.. python casual_bayesian_train.py \
    --dataset_name xsum \
    --start 0 \
    --end 5 \
    --max_retries 5
```

---

## Baseline Methods

BIRD baseline methods are in `code/run/scenario_*.py` and `code/baselines/`:

```bash
# BIRD methods
PYTHONPATH=.. python scenario_analysis.py
PYTHONPATH=.. python scenario_inference.py
PYTHONPATH=.. python scenario_train.py
```

For other baseline methods, see scripts in `code/baselines/`. Evaluation scripts are in `code/evaluation/`.

---

## FAQ

### 1. `ModuleNotFoundError: No module named 'utils'`

Make sure `PYTHONPATH` is set:

```bash
PYTHONPATH=.. python <script_name>.py
```

### 2. `OSError: [Errno 24] Too many open files`

The httpx connection pool is already configured with limits in `utils.py`. If you still encounter this, increase the system file descriptor limit:

```bash
ulimit -n 65536
```

### 3. `sentence_transformers` fails to load the model

Ensure:
- You are using `sentence-transformers>=5.0.0`
- The model has been downloaded to the path specified by `MiniLM_L6_PATH` in `config.py`
- The path is a directory containing `config.json`

### 4. Filename mismatch between stages

Each stage looks for files with the `_0_1000_` naming pattern by default. If your `--start`/`--end` arguments differ, create symlinks (see instructions under each stage).

### 5. API call timeouts or failures

- Built-in automatic retry mechanisms are included in the code
- Adjust retry count via `--max_retries`
- Verify that `base_url` and `api_key` in `config.py` are correct

---

## Quick Reproduction (5 samples)

Below is the complete command sequence for a quick end-to-end run using the common2sense dataset:

```bash
# 0. Install dependencies and configure
pip install -r requirements.txt
# Edit code/utils/config.py to set API key, model path, etc.

# 1. Enter the run directory
cd code/run
mkdir -p results

# 2. Stage 1: Factor generation
PYTHONPATH=.. python iterative_factor_gen.py --start 0 --end 5 --cluster

# 3. Create symlink (required by Stage 2)
cd results
ln -sf common2sense_gpt-4o-mini_0_5_factors.json common2sense_gpt-4o-mini_0_1000_factors_processed_lowercased.json
cd ..

# 4. Stage 2: Condition mapping
PYTHONPATH=.. python hierarchical_condition_mapping.py --start 0 --end 5 --enable_self_reflection --max_retries 5

# 5. Create symlink (required by Stage 3)
cd results
ln -sf common2sense_gpt-4o-mini_0_5_condition_mapping.json common2sense_gpt-4o-mini_0_1000_condition_mapping.json
cd ..

# 6. Stage 3: Probabilistic inference
PYTHONPATH=.. python casual_bayesian_train.py --start 0 --end 5 --max_retries 5

# 7. Evaluation (optional, requires human annotation data)
PYTHONPATH=.. python evaluate_nb_cbn.py --start 0 --end 5
```

> **Estimated runtime (5 samples):**
> - Stage 1: ~15-30 minutes (depends on API speed)
> - Stage 2: ~15-25 minutes
> - Stage 3: ~5-10 minutes
> - Total: ~35-65 minutes
