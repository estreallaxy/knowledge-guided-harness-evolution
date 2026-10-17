#!/usr/bin/env bash
set -e

if [ "$#" -ne 4 ]; then
  echo "Usage: bash scripts/run_ruler.sh <model> <query-aware|query-agnostic> <0.6|0.7|0.8|0.9> <4k|32k>"
  echo "Models: Llama-3.1-8B-Instruct, Qwen-2.5-7B-Instruct"
  exit 1
fi

MODEL_NAME="$1"
COMPRESSION_SETTING="$2"
COMPRESSION_RATIO="$3"
CONTEXT_LENGTH="$4"

case "$MODEL_NAME" in
  Llama-3.1-8B-Instruct)
    MODEL="meta-llama/Llama-3.1-8B-Instruct"
    ;;
  Qwen-2.5-7B-Instruct)
    MODEL="Qwen/Qwen2.5-7B-Instruct"
    ;;
  *)
    echo "Unknown model: $MODEL_NAME"
    exit 1
    ;;
esac

case "$COMPRESSION_SETTING" in
  query-aware)
    QUERY_AWARE="true"
    ;;
  query-agnostic)
    QUERY_AWARE="false"
    ;;
  *)
    echo "Unknown compression setting: $COMPRESSION_SETTING"
    exit 1
    ;;
esac

case "$COMPRESSION_RATIO" in
  0.6|0.7|0.8|0.9)
    ;;
  *)
    echo "Unsupported compression rate: $COMPRESSION_RATIO"
    exit 1
    ;;
esac

case "$CONTEXT_LENGTH" in
  4k)
    DATA_DIR="4096"
    MAX_CONTEXT_LENGTH="4096"
    ;;
  32k)
    DATA_DIR="32768"
    MAX_CONTEXT_LENGTH="32768"
    ;;
  *)
    echo "Unsupported context length: $CONTEXT_LENGTH"
    exit 1
    ;;
esac

cd "$(dirname "$0")/.."

PRESS_NAMES=(
  h2o
  obcache_k_h2o
  tova
  obcache_k_tova
  snapkv
  obcache_k_snapkv
  adakv_snapkv
  adakv_obcache_k_snapkv
)

for PRESS_NAME in "${PRESS_NAMES[@]}"; do
  echo "Running RULER ${DATA_DIR}: model=${MODEL_NAME}, press=${PRESS_NAME}, compression_ratio=${COMPRESSION_RATIO}, query_aware=${QUERY_AWARE}"
  python evaluation/evaluate.py \
    --config_file /dev/null \
    --dataset ruler \
    --data_dir "$DATA_DIR" \
    --model "$MODEL" \
    --press_name "$PRESS_NAME" \
    --compression_ratio "$COMPRESSION_RATIO" \
    --max_context_length "$MAX_CONTEXT_LENGTH" \
    --query_aware "$QUERY_AWARE"
done
