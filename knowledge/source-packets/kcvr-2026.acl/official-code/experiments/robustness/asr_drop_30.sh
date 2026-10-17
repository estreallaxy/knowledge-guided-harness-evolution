#!/bin/bash
# Robustness Test: ASR-Drop (30% sentence removal)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "Running Robustness Test: ASR-Drop (30%)"
echo "========================================"

OUTPUT_DIR="experiments/paper_results/robustness/asr_drop_30"
mkdir -p "$OUTPUT_DIR"

MODEL_PATH="${MODEL_PATH:-models/checkpoints/internvl_kcvr_micro_v2_7subj_full}"

if [ ! -d "$MODEL_PATH" ]; then
    echo "⚠ Warning: Model not found at $MODEL_PATH"
    echo "Please train the model first or set MODEL_PATH environment variable"
    exit 1
fi

# Apply ASR-Drop corruption to transcripts
# This script modifies transcripts by randomly removing 30% of sentence boundaries
python scripts/corrupt_transcripts.py \
    --input-dir data/annotations/standard_labels/micro \
    --output-dir "$OUTPUT_DIR/corrupted_labels" \
    --corruption-type asr_drop \
    --drop-ratio 0.3

# Run inference with corrupted transcripts
python src/stage3_inference/infer_micro.py \
    --model-path "$MODEL_PATH" \
    --dataset data/splits/v2_7subj_trainvaltest.json \
    --split test \
    --labels-root "$OUTPUT_DIR/corrupted_labels" \
    --output-dir "$OUTPUT_DIR/predictions"

# Run evaluation
python src/stage3_inference/evaluate.py \
    --predictions "$OUTPUT_DIR/predictions/predictions_micro.jsonl" \
    --labels-root data/annotations/standard_labels/micro \
    --plans-root cache/plans/micro_plans \
    --kg-csv-root knowledge_graph/raw_csv \
    --output-dir "$OUTPUT_DIR/metrics" \
    --level micro

echo "ASR-Drop test complete. Results saved to $OUTPUT_DIR"

