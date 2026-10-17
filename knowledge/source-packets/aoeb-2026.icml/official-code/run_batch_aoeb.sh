#!/usr/bin/env bash
set -euo pipefail

# Edit these defaults directly for common AOEB runs.
MODEL="jina-v4"
TASK_CONFIG_LIST=(
    "aoeb_ng/tasks/MMRC-R-session-it-pair.json"
    "aoeb_ng/tasks/MMRC-R-session-vision-doc.json"
    "aoeb_ng/tasks/MMRC-R-round-it-pair.json"
)
TASK_CONFIGS=$(IFS=,; echo "${TASK_CONFIG_LIST[*]}")
OUTPUT_DIR="./results"
BATCH_SIZE=4
GPU_ID=0
MAX_LENGTH=8192

# Positional overrides:
#   $1 model
#   $2 comma-separated task configs; empty string keeps defaults
#   $3 output dir
#   $4 batch size
#   $5 GPU id for CUDA_VISIBLE_DEVICES
#   $6 max length
MODEL=${1:-$MODEL}
TASK_CONFIGS=${2:-$TASK_CONFIGS}
OUTPUT_DIR=${3:-$OUTPUT_DIR}
BATCH_SIZE=${4:-$BATCH_SIZE}
GPU_ID=${5:-$GPU_ID}
MAX_LENGTH=${6:-$MAX_LENGTH}

if [[ $# -lt 6 ]]; then
    case "$MODEL" in
        vista)
            MAX_LENGTH=512
            ;;
    esac
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python}"
LOG_DIR="$SCRIPT_DIR/logs"

mkdir -p "$LOG_DIR"
export CUDA_VISIBLE_DEVICES="$GPU_ID"

MODEL_TAG="$(basename "$MODEL")"
MODEL_TAG="${MODEL_TAG//[^[:alnum:]_.-]/_}"
LOG_FILE="$LOG_DIR/run_aoeb_batch_${MODEL_TAG}_$(date +%Y%m%d_%H%M%S).log"

echo "Running AOEB batch evaluation"
echo "Model: $MODEL"
echo "Task configs: $TASK_CONFIGS"
echo "Output dir: $OUTPUT_DIR"
echo "Batch size: $BATCH_SIZE"
echo "GPU: $GPU_ID"
echo "Max length: $MAX_LENGTH"
echo "Log file: $LOG_FILE"

CMD=(
    "$PYTHON_BIN" "$SCRIPT_DIR/run_batch_aoeb.py"
    --model "$MODEL"
    --task-configs "$TASK_CONFIGS"
    --output-dir "$OUTPUT_DIR"
    --batch-size "$BATCH_SIZE"
    --gpu-id "$GPU_ID"
    --max-length "$MAX_LENGTH"
)

"${CMD[@]}" >>"$LOG_FILE" 2>&1 &
echo "PID: $!"
