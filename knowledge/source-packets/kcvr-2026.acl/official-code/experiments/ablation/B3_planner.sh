#!/bin/bash
# Ablation B3: + SG-Planner

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "Running Ablation B3: + SG-Planner"
echo "=================================="

OUTPUT_DIR="experiments/paper_results/ablation/B3"
mkdir -p "$OUTPUT_DIR"

CONFIG_FILE="experiments/configs/ablation/B3_planner.yaml"
MODEL_PATH="${MODEL_PATH:-models/checkpoints/internvl_kcvr_B3}"

if [ ! -d "$MODEL_PATH" ]; then
    echo "⚠ Warning: Model not found at $MODEL_PATH"
    echo "Please train the model first or set MODEL_PATH environment variable"
    exit 1
fi

# Run inference
python src/stage3_inference/infer_micro.py \
    --model-path "$MODEL_PATH" \
    --dataset data/splits/v2_7subj_trainvaltest.json \
    --split test \
    --output-dir "$OUTPUT_DIR/predictions"

# Run evaluation
python src/stage3_inference/evaluate.py \
    --predictions "$OUTPUT_DIR/predictions/predictions_micro.jsonl" \
    --labels-root data/annotations/standard_labels/micro \
    --plans-root cache/plans/micro_plans \
    --kg-csv-root knowledge_graph/raw_csv \
    --output-dir "$OUTPUT_DIR/metrics" \
    --level micro

echo "B3 ablation complete. Results saved to $OUTPUT_DIR"

