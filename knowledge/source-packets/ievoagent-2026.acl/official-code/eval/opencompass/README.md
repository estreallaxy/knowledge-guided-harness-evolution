# OpenCompass Evaluation

This directory contains custom evaluation configs for running MT-Bench-101 evaluations with our IEvoAgent and baseline models.

## Setup

```bash
# Install OpenCompass framework
pip install opencompass

# Or install from source for the latest version:
# git clone https://github.com/open-compass/opencompass.git
# cd opencompass && pip install -e .
```

## Structure

- `configs/` — Custom evaluation configs for MT-Bench-101
  - `eval_subjective_mtbench101_*.py` — Configs for different models (ours, baselines, GPT-4, Llama, Qwen, etc.)
  - `eval_chat_agent.py` / `eval_chat_agent_baseline.py` — Agent-based eval configs
- `models/customAgent.py` — Custom model adapter for IEvoAgent in OpenCompass
- `data/subjective/mtbench101.jsonl` — MT-Bench-101 dataset
- `myrun.sh` — Quick launch script for evaluation

## Usage

```bash
# Run evaluation with a specific config
python run.py configs/eval_subjective_mtbench101_myagent.py
```
