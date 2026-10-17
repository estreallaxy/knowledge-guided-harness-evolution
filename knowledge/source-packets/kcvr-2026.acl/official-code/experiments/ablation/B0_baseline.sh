#!/bin/bash
# Ablation B0: Baseline (InternVL-SFT, no planning)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "Running Ablation B0: Baseline"
echo "=============================="

OUTPUT_DIR="experiments/paper_results/ablation/B0"
mkdir -p "$OUTPUT_DIR"

# Configuration: No planning, no visual attention, no constraints
CONFIG_FILE="experiments/configs/ablation/B0_baseline.yaml"

# Note: This requires a trained model with B0 configuration
# For full reproduction, train the model first:
# llamafactory-cli train "$CONFIG_FILE"

MODEL_PATH="${MODEL_PATH:-models/checkpoints/internvl_kcvr_B0}"

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

echo "B0 ablation complete. Results saved to $OUTPUT_DIR"

