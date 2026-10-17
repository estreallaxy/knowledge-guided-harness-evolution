#!/usr/bin/env bash
set -e

if [ "$#" -lt 4 ]; then
  echo "Usage: bash scripts/run_longbench.sh <model> <query-aware|query-agnostic> <0.6|0.7|0.8|0.9> <task-groups>"
  echo "Models: Llama-3.1-8B-Instruct, Qwen-2.5-7B-Instruct"
  echo "Task groups: qa, summ, fewshot, synthetic, code, all"
  echo "Example: bash scripts/run_longbench.sh Llama-3.1-8B-Instruct query-aware 0.8 qa code summ"
  echo "Example: bash scripts/run_longbench.sh Qwen-2.5-7B-Instruct query-agnostic 0.7 tasks=qa,code,summ"
  exit 1
fi

MODEL_NAME="$1"
COMPRESSION_SETTING="$2"
COMPRESSION_RATIO="$3"
TASK_GROUP_INPUT="${*:4}"

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

TASKS=()
TASK_GROUPS="${TASK_GROUP_INPUT#tasks=}"
TASK_GROUPS="${TASK_GROUPS//,/ }"

for TASK_GROUP in $TASK_GROUPS; do
  case "$TASK_GROUP" in
    qa)
      TASKS+=(narrativeqa qasper multifieldqa_en hotpotqa 2wikimqa musique)
      ;;
    summ)
      TASKS+=(gov_report qmsum multi_news)
      ;;
    fewshot)
      TASKS+=(trec triviaqa samsum)
      ;;
    synthetic)
      TASKS+=(passage_count passage_retrieval_en)
      ;;
    code)
      TASKS+=(lcc repobench-p)
      ;;
    all)
      TASKS+=(
        narrativeqa qasper multifieldqa_en hotpotqa 2wikimqa musique
        gov_report qmsum multi_news
        trec triviaqa samsum
        passage_count passage_retrieval_en
        lcc repobench-p
      )
      ;;
    *)
      echo "Unknown task group: $TASK_GROUP"
      exit 1
      ;;
  esac
done

for TASK in "${TASKS[@]}"; do
  for PRESS_NAME in "${PRESS_NAMES[@]}"; do
    echo "Running LongBench ${TASK}: model=${MODEL_NAME}, press=${PRESS_NAME}, compression_ratio=${COMPRESSION_RATIO}, query_aware=${QUERY_AWARE}"
    python evaluation/evaluate.py \
      --config_file /dev/null \
      --dataset longbench \
      --data_dir "$TASK" \
      --model "$MODEL" \
      --press_name "$PRESS_NAME" \
      --compression_ratio "$COMPRESSION_RATIO" \
      --query_aware "$QUERY_AWARE"
  done
done
