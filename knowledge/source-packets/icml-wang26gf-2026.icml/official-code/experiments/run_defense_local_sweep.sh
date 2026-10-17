#!/bin/bash
# Defense evaluation sweep across local models
set -e
cd /home/coder-gw/Projects/ROA-LLM
export PYTHONPATH=.

MODELS=(
    "qwen2.5-coder:1.5b"
    "qwen3:4b"
    "qwen2.5-coder:7b"
    "qwen3:8b"
    "qwen2.5-coder:14b"
    "mixtral:8x7b"
)

for model in "${MODELS[@]}"; do
    echo ""
    echo "=========================================="
    echo "Defense Evaluation: $model"
    echo "=========================================="
    python experiments/real_defense_evaluation.py \
        --model "$model" --provider ollama --seeds 5 \
        --judge-model gemini-2.0-flash-lite --judge-provider google \
        --output-dir data/results/defense_local_sweep
done

echo ""
echo "=== ALL DEFENSE SWEEPS DONE ==="
