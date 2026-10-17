#!/usr/bin/env bash
set -euo pipefail

TASK="aime25_1"
BASE="aime25_1_results/skythought_evals_models_Qwen_Qwen3-4B_4bit_aime25_1_70a749"
BUDGETS=(2000 6000 10000 14000 18000 22000 26000 30000)
GROUP_SIZES=(2 4 8 16 32)
TRIALS=32

for TOK in "${BUDGETS[@]}"; do
  RUN_DIR="${BASE}/truncate_${TOK}"
  for G in "${GROUP_SIZES[@]}"; do
    echo "▶ g=$G  trials=$TRIALS  dir=${RUN_DIR}"
    skythought score-majority \
        --task "$TASK" \
        --run-dir "$RUN_DIR" \
        --group-size "$G" \
        --num-trials "$TRIALS"
  done
done
echo "✅ majority voting finished for all truncations."
