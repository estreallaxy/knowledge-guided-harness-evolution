#!/usr/bin/env bash
set -euo pipefail

# Defaults; override via env or edit here
TASK="${TASK:-aime25_1}"
BASE="${BASE:-aime25_1_results/Qwen_Qwen3-4B_aime25_1_29ebc7}"
BUDGETS=(${BUDGETS_OVERRIDE:-2000 6000 10000 14000 18000 22000 26000 30000})
GROUP_SIZES=(${GROUP_SIZES_OVERRIDE:-2 4 8 16 32})
TRIALS="${TRIALS:-32}"
PRM_MODEL_ID="${PRM_MODEL_ID:-sail/ActPRM-X}"
BATCH_SIZE="${BATCH_SIZE:-1}"
DTYPE="${DTYPE:-auto}"   # auto|bf16|fp16|fp32
DEVICE="${DEVICE:-auto}" # auto|cuda|cpu

echo "▶ PRM best-of-N | task=$TASK base=$BASE trials=$TRIALS model=$PRM_MODEL_ID dtype=$DTYPE device=$DEVICE"

for TOK in "${BUDGETS[@]}"; do
  RUN_DIR="${BASE}/truncate_${TOK}"
  for G in "${GROUP_SIZES[@]}"; do
    echo "▶ g=$G  trials=$TRIALS  dir=${RUN_DIR}"
    python3 score_prm_bestof.py \
      --run-dir "$RUN_DIR" \
      --group-size "$G" \
      --num-trials "$TRIALS" \
      --prm-model-id "$PRM_MODEL_ID" \
      --batch-size "$BATCH_SIZE" \
      --dtype "$DTYPE" \
      --device "$DEVICE" \
      --write-scores-cache
  done
done
echo "✅ PRM best-of-N finished for all truncations."


