# LLM Collusion Experiments for the Bertrand Pricing Game

This repository reproduces experiments from our [ICML 2026 Paper](https://openreview.net/pdf?id=Vhi9tHbKTa). This includes price competition experiments for the Bertrand game that test collusive behavior in LLM reasoning models across different prompting styles and with activation steering. 

```
@inproceedings{CollusiveReasoningAgents,
    title={Position: Collusion Risks Among AI Reasoning Agents Justify Certification Requirements for Making Market Decisions},   
    author={Riemer, Matthew and Tosato, Tommaso and Memarian, Amin and Touzel, Maximilian Puelma and Berseth, Glen and Rish, Irina and Dumas, Guillaume},    
    booktitle={In International Conference on Machine Learning (ICML)},    
    year={2026}   
}
```

## Project Structure

```
├── environment/           # Game environment implementations
├── steering/              # Steering vector training and full steering experiments
│   └── lib/              # Shared library for activation extraction and CAA training
├── partial_steering/      # Partial steering experiments (subset of agents steered)
├── judges/                # LLM-as-judge behavior scoring scripts
└── results/
    ├── datasets/          # Training data for steering vectors
    └── steering_vectors/  # Pre-trained steering vectors
```

## Dependencies

- `vllm` — Inference engine for local models
- `transformers` — For behavior steering experiments (direct model access)
- `torch`
- `numpy`, `scipy`
- `pandas` — For judge scoring output
- `openai`, `python-dotenv` — For ChatGPT tester

## environment/

Core Bertrand competition game engines.

- `oligopoly.py` — Duopoly (2-agent) game environment
- `multiprompt_oligopoly.py` — Triopoly (3-agent) game environment with per-agent prompts

## Prompt Variants

The `prefix` argument controls the system prompt given to each agent. Variants can be combined (e.g., `P0+B`, `P0+BT`).

**Base prompts:**

| Prefix | Description |
|--------|-------------|
| `P0` | Default prompt to maximize profit |
| `PI` | Implicit prompt to collude |
| `PC` | Explicit prompt to collude |

**Anti-collusion prompts:**

| Prefix | Description |
|--------|-------------|
| `AC` | Prompt to maximize profit and avoid collusion |
| `CD` | Prompt to maximize profit and avoid collusion, including the Wikipedia definition of a cartel |
| `AP` | Prompt to maximize profit and avoid collusion and penalties |

**Alternative objective prompts:**

| Prefix | Description |
|--------|-------------|
| `MD` | Prompt to maximize demand |
| `NPA` | Prompt to minimize prices |
| `NPB` | Prompt to minimize profit |

**Monitoring modifiers (append to a base prompt, e.g., `P0+B`):**

| Modifier | Description |
|----------|-------------|
| `+B` | Adds notice that behavior will be monitored |
| `+T` | Adds notice that thoughts will be monitored |
| `+BT` | Adds notice that behavior and thoughts will be monitored |


## Price Scale Values

The `price_scale` parameter (alpha) scales the price space in the Bertrand competition. Higher values stretch the price range proportionally, testing whether collusive behavior persists across different price magnitudes.

| Scale | Description |
|-------|-------------|
| 1.0   | Default — prices around cost of 1 |
| 3.2   | Moderate scaling |
| 10.0  | High scaling |

## Basic Experiments

### r1_duopoly_tester.py

Baseline 2-agent Bertrand competition with DeepSeek-R1.

```bash
python r1_duopoly_tester.py <prefix> <prior_steps> <size> [price_scale]
```

| Argument | Description |
|----------|-------------|
| `prefix` | Prompt variant (see [Prompt Variants](#prompt-variants)) |
| `prior_steps` | Number of synthetic history steps around the Nash equilibria (always 1 in our paper) |
| `size` | Model size (`7B`, `14B`, `32B`) |
| `price_scale` | (Optional) Price scale multiplier, default `1.0` |

**Examples:**
```bash
# Run with default prompt, 1 history step, 7B model, default price scale
python r1_duopoly_tester.py P0 1 7B

# Same but with moderate price scaling (3.2x)
python r1_duopoly_tester.py P0 1 7B 3.2

# Same but with high price scaling (10x)
python r1_duopoly_tester.py P0 1 7B 10.0
```

### r1_triopoly_tester.py

Baseline 3-agent Bertrand competition with DeepSeek-R1. Each agent can receive a different prompt variant via comma-separated prefixes.

```bash
python r1_triopoly_tester.py <prefix> <prior_steps> <size>
```

| Argument | Description |
|----------|-------------|
| `prefix` | Comma-separated prompt variants, one per agent (e.g., `P0,P0,P0`) |
| `prior_steps` | Number of synthetic history steps around the Nash equilibria (always 1 in our paper) |
| `size` | Model size (`7B`, `14B`, `32B`) |

**Examples:**
```bash
# All three agents get the default prompt
python r1_triopoly_tester.py P0,P0,P0 1 7B

# Mixed prompts: agent 2 gets a different variant
python r1_triopoly_tester.py P0,P3,P0 1 14B
```

### chatgpt_duopoly_tester.py

2-agent Bertrand competition using OpenAI reasoning models (o3, o4-mini, gpt-5.4, etc.) via the Responses API. Requires `OPENAI_API_KEY` in environment or `.env` file.

```bash
python chatgpt_duopoly_tester.py [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--prefix` | `P0` | Prompt variant (see [Prompt Variants](#prompt-variants)) |
| `--prior_steps` | `1` | Number of synthetic history steps around the Nash equilibria (always 1 in our paper) |
| `--model` | `gpt-5.4` | OpenAI model name |
| `--reasoning_summary` | `auto` | Reasoning verbosity: `auto`, `concise`, `detailed` |
| `--reasoning_effort` | `medium` | Compute budget: `low`, `medium`, `high` |
| `--temperature` | `1.0` | Sampling temperature |
| `--rounds` | `300` | Game rounds per episode |
| `--seed` | (all) | Run a single episode seed (0-9), or omit for all 10 |
| `--max_retries` | `2` | Retries per failed generation |
| `--overwrite` | off | Overwrite existing output instead of resuming |

**Examples:**
```bash
# Run with o3 model at high reasoning effort
python chatgpt_duopoly_tester.py --model o3 --reasoning_effort high

# Run a single episode (seed 0) with o4-mini and collusion prompt
python chatgpt_duopoly_tester.py --model o4-mini --prefix PC --seed 0

# Run with detailed reasoning summaries for 100 rounds
python chatgpt_duopoly_tester.py --model gpt-5.4 --reasoning_summary detailed --rounds 100
```

## steering/

This directory contains both the steering vector training pipeline and the full steering experiments.

### Training Steering Vectors

#### train_steering_vectors.py

Trains Contrastive Activation Addition (CAA) steering vectors. Extracts activations from all model layers, computes direction vectors that separate high-collusion from low-collusion behavior, and generates analysis visualizations.

```bash
python steering/train_steering_vectors.py [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--dataset` | — | Dataset name (loads from `results/datasets/{name}_high_scores_behavior.jsonl` and `_low_scores_behavior.jsonl`) |
| `--list-datasets` | — | List all available datasets and exit |
| `--high-data` | — | Custom path to high-collusion JSONL (overrides `--dataset`) |
| `--low-data` | — | Custom path to low-collusion JSONL (overrides `--dataset`) |
| `--model` | `deepseek-ai/DeepSeek-R1-Distill-Qwen-7B` | Model to extract activations from |
| `--max-pairs` | all | Maximum number of prompt-thought pairs to use |
| `--layers` | all | Specific layers to extract (space-separated) |
| `--no-normalize` | off | Don't normalize vectors to unit length |
| `--output-dir` | `results/steering_vectors` | Output directory |
| `--output-name` | dataset name | Name for this training run |
| `--load-activations` | — | Path to pre-computed activations (skip extraction) |
| `--skip-save-activations` | off | Don't save intermediate activations |
| `--no-visualize` | off | Skip visualization generation |
| `--top-n` | `5` | Number of top layers to visualize in detail |

**Examples:**
```bash
# List available datasets
python steering/train_steering_vectors.py --list-datasets

# Train with the included behavior dataset (default model)
python steering/train_steering_vectors.py --dataset max_profits_behavior

# Train with a custom model and limited pairs
python steering/train_steering_vectors.py --dataset max_profits_behavior --model Qwen/Qwen3-14B --max-pairs 100

# Train with custom data files
python steering/train_steering_vectors.py --high-data path/to/high.jsonl --low-data path/to/low.jsonl --output-name custom_run

# Train specific layers only, skip visualizations
python steering/train_steering_vectors.py --dataset max_profits_behavior --layers 10 11 12 13 14 --no-visualize
```

Output is saved to `results/steering_vectors/{output-name}/`, including:
- `vectors.json` — trained steering vectors for all layers
- `metrics.json` — per-layer performance metrics
- `plots/` — visualization plots (if enabled)

#### analyze_layers.py

Analyzes and compares layer-wise CAA performance from training metrics. Useful for identifying the optimal steering layer.

```bash
python steering/analyze_layers.py --metrics <path_to_metrics.json> [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--metrics` | (required) | Path(s) to metrics JSON file(s) from training |
| `--compare` | off | Compare multiple metrics files side-by-side |
| `--names` | — | Display names for each metrics file (for comparison) |
| `--top-n` | `10` | Number of top layers to display |
| `--visualize` | off | Generate visualization plots |
| `--output` | same as metrics | Output directory for visualizations |

**Examples:**
```bash
# Analyze a single training run
python steering/analyze_layers.py --metrics results/steering_vectors/max_profits_behavior/metrics.json

# Show only top 5 layers
python steering/analyze_layers.py --metrics results/steering_vectors/max_profits_behavior/metrics.json --top-n 5

# Compare two training runs
python steering/analyze_layers.py --compare \
    --metrics results/steering_vectors/run_a/metrics.json results/steering_vectors/run_b/metrics.json \
    --names "Run A" "Run B"

# Generate visualizations
python steering/analyze_layers.py --metrics results/steering_vectors/max_profits_behavior/metrics.json --visualize --output plots/
```

#### Training Data

Pre-labeled behavior data for training steering vectors is in `results/datasets/`:

- `max_profits_high_scores_behavior.jsonl` — Transcripts scored as highly collusive
- `max_profits_low_scores_behavior.jsonl` — Transcripts scored as non-collusive

Each JSONL file contains experiment transcripts with agent thoughts, used as contrastive pairs for CAA.

---

### Steering Experiments

Full activation steering experiments where all agents are steered using pre-trained behavior vectors.

### r1_duopoly_all_steering_behavior.py

2-agent DeepSeek-R1 with all agents steered via behavior vectors.

```bash
python steering/r1_duopoly_all_steering_behavior.py <prefix> <prior_steps> <size> <multiplier> <seed> [price_scale] [layer1] [layer2] ...
```

| Argument | Description |
|----------|-------------|
| `prefix` | Prompt variant (see [Prompt Variants](#prompt-variants)) |
| `prior_steps` | Number of synthetic history steps around the Nash equilibria (always 1 in our paper) |
| `size` | Model size (`7B`, `14B`, `32B`) |
| `multiplier` | Steering vector multiplier (strength of steering) |
| `seed` | Random seed for reproducibility |
| `price_scale` | (Optional) Price scale, default `1.0` |
| `layer1, ...` | (Optional) Model layers to steer, default `[12]` |

**Examples:**
```bash
# Steer with multiplier 1.0, seed 42, default price scale and layer
python steering/r1_duopoly_all_steering_behavior.py P0 1 7B 1.0 42

# Same but with moderate price scaling (3.2x)
python steering/r1_duopoly_all_steering_behavior.py P0 1 7B 1.0 42 3.2

# Same but with high price scaling (10x)
python steering/r1_duopoly_all_steering_behavior.py P0 1 7B 1.0 42 10.0

# Steer at layers 12 and 18 (must specify price_scale to pass layers)
python steering/r1_duopoly_all_steering_behavior.py P0 1 7B 1.0 42 1.0 12 18
```

### r1_triopoly_all_steering_behavior.py

3-agent DeepSeek-R1 with all agents steered. Same interface as the duopoly version.

**Examples:**
```bash
python steering/r1_triopoly_all_steering_behavior.py P0 1 7B 1.0 42
```

### qwen3_duopoly_steering_behavior.py

2-agent Qwen3 with all agents steered. Uses model-specific layer selections and steering vectors from `results/steering_vectors/{model}/custom/vectors.json`.

```bash
python steering/qwen3_duopoly_steering_behavior.py <model_name> <multiplier> <seed>
```

| Argument | Description |
|----------|-------------|
| `model_name` | Qwen3 model size (`Qwen3-0.6B`, `Qwen3-1.7B`, `Qwen3-4B`, `Qwen3-8B`, `Qwen3-14B`, `Qwen3-32B`) |
| `multiplier` | Steering vector multiplier (strength of steering) |
| `seed` | Random seed for reproducibility |

**Examples:**
```bash
# Steer Qwen3-14B with multiplier 10.0
python steering/qwen3_duopoly_steering_behavior.py Qwen3-14B 10.0 42

# Steer Qwen3-32B with stronger multiplier
python steering/qwen3_duopoly_steering_behavior.py Qwen3-32B 50.0 0
```

## partial_steering/

Partial steering experiments where only a subset of agents are steered. This tests whether collusive behavior propagates from steered agents to unsteered agents. Same interface as `steering/r1_duopoly_all_steering_behavior.py`.

### r1_duopoly_1of2_steering_behavior.py

2-agent DeepSeek-R1 with only 1 of 2 agents steered.

**Examples:**
```bash
# Steer 1 agent with default price scale
python partial_steering/r1_duopoly_1of2_steering_behavior.py P0 1 7B 1.0 42

# With moderate price scaling
python partial_steering/r1_duopoly_1of2_steering_behavior.py P0 1 7B 1.0 42 3.2

# With high price scaling
python partial_steering/r1_duopoly_1of2_steering_behavior.py P0 1 7B 1.0 42 10.0
```

### r1_triopoly_1of3_steering_behavior.py

3-agent DeepSeek-R1 with only 1 of 3 agents steered.

**Examples:**
```bash
python partial_steering/r1_triopoly_1of3_steering_behavior.py P0 1 7B 1.0 42
```

### r1_triopoly_2of3_steering_behavior.py

3-agent DeepSeek-R1 with 2 of 3 agents steered.

**Examples:**
```bash
python partial_steering/r1_triopoly_2of3_steering_behavior.py P0 1 7B 1.0 42
```

## judges/

LLM-as-judge scripts that score agent behavior from experiment outputs. Each script loads experiment transcripts and uses a language model to assign collusion scores (1-10) to each agent's behavior.

All judges share a common interface (all arguments are optional with sensible defaults):

```bash
python judges/<script>.py [model_or_tag] [batch_size] [test_limit] [temperatures] [seed] [run_mode] [failed_csv]
```

| Argument | Default | Description |
|----------|---------|-------------|
| `model_or_tag` | varies | Model name or run tag (depends on script, see below) |
| `batch_size` | varies | Prompts per GPU batch (adjust based on available memory) |
| `test_limit` | `0` | Process only first N data points (`0` = process all) |
| `temperatures` | `0.3` | Comma-separated temperature values for scoring |
| `seed` | `12345` | RNG seed for reproducibility |
| `run_mode` | `steering` | Which experiments to score: `steering`, `baseline`, or `all` |
| `failed_csv` | (none) | Path to a failed scores CSV to rerun only missing scores |

### r1_warden_behscoring.py

Judge using DeepSeek-R1-Distill-Qwen-7B. No model argument needed (hardcoded).

**Examples:**
```bash
# Score steering experiments with all defaults
python judges/r1_warden_behscoring.py

# Score baseline experiments with batch size 256
python judges/r1_warden_behscoring.py 256 0 "0.3" 12345 baseline
```

### llama33_warden_behscoring.py

Judge using Llama-3.3-70B-Instruct. No model argument needed (hardcoded). Default batch size: 32 (large model).

**Examples:**
```bash
# Score with all defaults
python judges/llama33_warden_behscoring.py

# Score steering experiments with explicit settings
python judges/llama33_warden_behscoring.py 32 0 "0.3" 12345 steering
```

### qwen_warden_behscoring.py

Judge using Qwen3 models. First argument selects the model size.

**Examples:**
```bash
# Score using Qwen3-14B with defaults
python judges/qwen_warden_behscoring.py Qwen3-14B

# Score using Qwen3-32B, steering mode, batch size 256
python judges/qwen_warden_behscoring.py Qwen3-32B 256 0 "0.3" 12345 steering
```

### ministral_warden_behscoring.py

Judge using Ministral-3-14B-Instruct-2512. First argument is a run tag for output naming.

**Examples:**
```bash
# Score with default run tag
python judges/ministral_warden_behscoring.py

# Score with explicit run tag and settings
python judges/ministral_warden_behscoring.py ministral_3_14b 512 0 "0.3"
```

### olmo_warden_behscoring.py

Judge using OLMo-3.1-32B-Instruct. First argument is a run tag for output naming.

**Examples:**
```bash
# Score with default run tag
python judges/olmo_warden_behscoring.py

# Score with explicit run tag and settings
python judges/olmo_warden_behscoring.py olmo_3_1_32b 512 0 "0.3"
```

### olmo_think_warden_behscoring.py

Judge using OLMo-3.1-32B-Think (reasoning variant). First argument is a run tag for output naming.

**Examples:**
```bash
# Score with default run tag
python judges/olmo_think_warden_behscoring.py

# Score with explicit run tag and settings
python judges/olmo_think_warden_behscoring.py olmo_3_1_32b_think 512 0 "0.3"
```

### oss_warden_behscoring.py

Judge using OpenAI OSS models. First argument is the model version identifier.

**Examples:**
```bash
# Score using the 2025-04-16 model version with defaults
python judges/oss_warden_behscoring.py 2025-04-16

# Score baseline experiments with explicit settings
python judges/oss_warden_behscoring.py 2025-04-16 512 0 "0.3" 12345 baseline
```
