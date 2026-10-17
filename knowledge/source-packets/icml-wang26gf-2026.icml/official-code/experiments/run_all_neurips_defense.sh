#!/bin/bash
# Run all NeurIPS defense experiments sequentially
# Each saves to data/results/defense_neurips/
set -e
cd /home/coder-gw/Projects/ROA-LLM
export PYTHONPATH=.

echo "=== Experiment 1: GPT-4o-mini ==="
python experiments/real_defense_evaluation.py \
    --model gpt-4o-mini --provider openai --seeds 5 \
    --judge-model gemini-2.0-flash-lite --judge-provider google \
    --output-dir data/results/defense_neurips

echo ""
echo "=== Experiment 2: Claude-Sonnet-4 ==="
python experiments/real_defense_evaluation.py \
    --model claude-sonnet-4-20250514 --provider anthropic --seeds 5 \
    --judge-model gemini-2.0-flash-lite --judge-provider google \
    --output-dir data/results/defense_neurips

echo ""
echo "=== Experiment 3: Temporal Persistence (Claude + Gemini) ==="
python experiments/icml_temporal_persistence.py \
    --seeds 5 \
    --output-dir data/results/temporal_neurips

echo ""
echo "=== ALL DONE ==="
