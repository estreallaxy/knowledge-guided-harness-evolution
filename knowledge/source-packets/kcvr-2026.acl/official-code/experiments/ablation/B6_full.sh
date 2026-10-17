#!/bin/bash
# Ablation B6: Full Model (+ GKS-Fusion)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "Running Ablation B6: Full Model"
echo "================================"

OUTPUT_DIR="experiments/paper_results/ablation/B6"
mkdir -p "$OUTPUT_DIR"

CONFIG_FILE="experiments/configs/ablation/B6_full.yaml"
MODEL_PATH="${MODEL_PATH:-models/checkpoints/internvl_kcvr_micro_v2_7subj_full}"

if [ ! -d "$MODEL_PATH" ]; then
    echo "⚠ Warning: Model not found at $MODEL_PATH"
    echo "Please train the model first or set MODEL_PATH environment variable"
    exit 1
fi

# Micro-level inference
python src/stage3_inference/infer_micro.py \
    --model-path "$MODEL_PATH" \
    --dataset data/splits/v2_7subj_trainvaltest.json \
    --split test \
    --output-dir "$OUTPUT_DIR/predictions"

# Macro-level inference (with GKS-Fusion)
MACRO_MODEL="${MACRO_MODEL:-models/checkpoints/internvl_kcvr_macro_v2_7subj_full}"

python src/stage3_inference/infer_macro.py \
    --model-path "$MACRO_MODEL" \
    --micro-predictions "$OUTPUT_DIR/predictions/predictions_micro.jsonl" \
    --output-dir "$OUTPUT_DIR/predictions"

# Run evaluation
python src/stage3_inference/evaluate.py \
    --predictions "$OUTPUT_DIR/predictions/predictions_macro.jsonl" \
    --labels-root data/annotations/standard_labels/macro \
    --plans-root cache/plans/macro_gks \
    --kg-csv-root knowledge_graph/raw_csv \
    --output-dir "$OUTPUT_DIR/metrics" \
    --level macro

echo "B6 ablation complete. Results saved to $OUTPUT_DIR"

