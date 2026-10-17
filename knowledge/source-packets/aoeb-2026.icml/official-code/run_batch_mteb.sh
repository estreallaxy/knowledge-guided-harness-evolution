#!/usr/bin/env bash
set -euo pipefail

# Edit these defaults directly when you want to rerun a common evaluation.
# MODEL="VLM2Vec/VLM2Vec-V2.0"
# MODEL="Qwen/Qwen3-VL-Embedding-2B"
# MODEL="jinaai/jina-embeddings-v4"
# MODEL="Alibaba-NLP/gme-Qwen2-VL-2B-Instruct"
# MODEL="Alibaba-NLP/gme-Qwen2-VL-7B-Instruct"
# MODEL="TIGER-Lab/VLM2Vec-LoRA"
# 这里传bge-base触发的是vista，不是文本基座
# MODEL="BAAI/bge-base-en-v1.5"
# MODEL="intfloat/mmE5-mllama-11b-instruct"
# MODEL="Qwen/Qwen3-Embedding-8B"
# MODEL="nvidia/NV-Embed-v2"
# MODEL="intfloat/multilingual-e5-large-instruct"
# MODEL="intfloat/e5-mistral-7b-instruct"
MODEL="nomic-ai/nomic-embed-text-v2-moe"
# MODEL="Alibaba-NLP/gte-multilingual-base"
# MODEL="BAAI/bge-m3"
# MODEL="BAAI/bge-large-en-v1.5"
TASK_LIST=(
    "MuSiQueRetrieval"
    "ToolRetRetrieval"
    "LoCoMoRetrieval"
    "LongMemEvalRetrieval"
    "SRABenchRetrieval"
)
# TASK_LIST=(
#     "MuSiQueRetrieval"
#     "Design2CodeRetrieval"
#     "MVRBComposedScreenshotRetrieval"
#     "LoCoMoRetrieval"
#     "ToolRetRetrieval"
#     "MVRBScreenshotRetrieval"
#     "ReFocusRetrieval"
#     "ChartMimicRetrieval"
#     "LongMemEvalRetrieval"
#     "DUDERetrieval"
#     "SRABenchRetrieval"
# )
TASKS=$(IFS=,; echo "${TASK_LIST[*]}")
OUTPUT_DIR="./results"
BATCH_SIZE=32
GPU_ID=4
MAX_LENGTH=8192
VISTA_USE_TASK_PROMPT=false
BGE_M3_USE_TASK_PROMPT=false
BGE_LARGE_USE_TASK_PROMPT=false
NOMIC_USE_TASK_PROMPT=false

# Optional CLI overrides, so one-off runs still do not require editing this file.
MODEL=${1:-$MODEL}
TASKS=${2:-$TASKS}
OUTPUT_DIR=${3:-$OUTPUT_DIR}
BATCH_SIZE=${4:-$BATCH_SIZE}
GPU_ID=${5:-$GPU_ID}
MAX_LENGTH=${6:-$MAX_LENGTH}
VISTA_USE_TASK_PROMPT=${7:-$VISTA_USE_TASK_PROMPT}
BGE_M3_USE_TASK_PROMPT=${8:-$BGE_M3_USE_TASK_PROMPT}
BGE_LARGE_USE_TASK_PROMPT=${9:-$BGE_LARGE_USE_TASK_PROMPT}
NOMIC_USE_TASK_PROMPT=${10:-$NOMIC_USE_TASK_PROMPT}

if [[ $# -lt 4 ]]; then
    case "$MODEL" in
        nv-embed-v2|nvembed|NV-Embed-v2|*NV-Embed-v2*|*nv-embed-v2*)
            BATCH_SIZE=1
            ;;
    esac
fi

if [[ $# -lt 6 ]]; then
    case "$MODEL" in
        bge-large-en-v1.5|BAAI/bge-large-en-v1.5|*bge-large-en-v1.5*)
            MAX_LENGTH=512
            ;;
        me5|m-e5|multilingual-e5-large-instruct|intfloat/multilingual-e5-large-instruct|*multilingual-e5-large-instruct*)
            MAX_LENGTH=512
            ;;
        nomic|nomic-v2-moe|nomic-embed-text-v2-moe|*nomic-embed-text-v2-moe*)
            MAX_LENGTH=512
            ;;
    esac
fi

EXTRA_ARGS=()
case "$VISTA_USE_TASK_PROMPT" in
    true|TRUE|1|yes|YES)
        EXTRA_ARGS+=(--vista-use-task-prompt)
        ;;
    false|FALSE|0|no|NO|"")
        ;;
    *)
        echo "Invalid VISTA_USE_TASK_PROMPT: $VISTA_USE_TASK_PROMPT (expected true or false)" >&2
        exit 2
        ;;
esac

case "$BGE_M3_USE_TASK_PROMPT" in
    true|TRUE|1|yes|YES)
        EXTRA_ARGS+=(--bge-m3-use-task-prompt)
        ;;
    false|FALSE|0|no|NO|"")
        ;;
    *)
        echo "Invalid BGE_M3_USE_TASK_PROMPT: $BGE_M3_USE_TASK_PROMPT (expected true or false)" >&2
        exit 2
        ;;
esac

case "$BGE_LARGE_USE_TASK_PROMPT" in
    true|TRUE|1|yes|YES)
        EXTRA_ARGS+=(--bge-large-use-task-prompt)
        ;;
    false|FALSE|0|no|NO|"")
        ;;
    *)
        echo "Invalid BGE_LARGE_USE_TASK_PROMPT: $BGE_LARGE_USE_TASK_PROMPT (expected true or false)" >&2
        exit 2
        ;;
esac

case "$NOMIC_USE_TASK_PROMPT" in
    true|TRUE|1|yes|YES)
        EXTRA_ARGS+=(--nomic-use-task-prompt)
        ;;
    false|FALSE|0|no|NO|"")
        ;;
    *)
        echo "Invalid NOMIC_USE_TASK_PROMPT: $NOMIC_USE_TASK_PROMPT (expected true or false)" >&2
        exit 2
        ;;
esac

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python}"
LOG_DIR="$SCRIPT_DIR/logs"

mkdir -p "$LOG_DIR"

export CUDA_VISIBLE_DEVICES="$GPU_ID"

echo "Running AOEB batch MTEB evaluation"
echo "Model: $MODEL"
echo "Tasks: $TASKS"
echo "Output dir: $OUTPUT_DIR"
echo "Batch size: $BATCH_SIZE"
echo "GPU: $GPU_ID"
echo "Max length: ${MAX_LENGTH:-model default}"
echo "VISTA use task prompt: $VISTA_USE_TASK_PROMPT"
echo "BGE-M3 use task prompt: $BGE_M3_USE_TASK_PROMPT"
echo "BGE-large use task prompt: $BGE_LARGE_USE_TASK_PROMPT"
echo "Nomic use task prompt: $NOMIC_USE_TASK_PROMPT"

MODEL_TAG="$(basename "$MODEL")"
MODEL_TAG="${MODEL_TAG//[^[:alnum:]_.-]/_}"

CMD=(
    "$PYTHON_BIN" "$SCRIPT_DIR/run_batch_mteb.py"
    --model "$MODEL"
    --tasks "$TASKS"
    --output-dir "$OUTPUT_DIR"
    --batch-size "$BATCH_SIZE"
)

if [[ -n "$MAX_LENGTH" ]]; then
    CMD+=(--max-length "$MAX_LENGTH")
fi
CMD+=("${EXTRA_ARGS[@]}")

"${CMD[@]}" >>"$LOG_DIR/run_mteb_batch_${MODEL_TAG}_$(date +%Y%m%d_%H%M%S).log" 2>&1 &