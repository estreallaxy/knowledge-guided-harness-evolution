#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Reproduce the newer/final historical metric file:
# crm_results/metrics_evalmode_sewsm_thinking_cuarewardbench-v0.4_Qwen3-VL-32B-Thinking.json
# Inferred config:
# - eval_mode: sewsm_thinking
# - prompt: osworld_sewsm_thinking.json
# - model_config/model: qwen3vl32b_thinking_tione_config / Qwen3-VL-32B-Thinking
# - max_screenshots: 20 (default; filename has no _maxS*)
# - exp_suffix: empty
#
# This script is also the shared benchmark launcher used by other preset wrappers.

PYTHON_BIN="${PYTHON_BIN:-python3}"
RUN_TITLE="${RUN_TITLE:-CUARewardBench Evaluation}"
MODEL_CONFIG="${MODEL_CONFIG:-qwen3vl32b_thinking_tione_config}"
EVAL_MODE="${EVAL_MODE:-sewsm_thinking}"
NUM_WORKERS="${NUM_WORKERS:-16}"
NUM_ITEMS="${NUM_ITEMS:-0}"
IMG_SCALE="${IMG_SCALE:-1.0}"
MAX_SCREENSHOTS="${MAX_SCREENSHOTS:-20}"
EXP_SUFFIX="${EXP_SUFFIX:-}"
OUTPUT_DIR="${OUTPUT_DIR:-${REPO_ROOT}/outputs/reproduce_qwen3vl32b_final_downloaded_data}"
ANNOTATION_FILE="${ANNOTATION_FILE:-${REPO_ROOT}/data/annotations/cuarewardbench-v0.4.json}"
TRAJECTORY_ROOT="${TRAJECTORY_ROOT:-${REPO_ROOT}/data/trajectories/osworld_verified}"
PROMPT_DIR="${PROMPT_DIR:-${REPO_ROOT}/configs/prompts}"
ONLY_METRIC="${ONLY_METRIC:-false}"

DEFAULT_TIMEOUT="${DEFAULT_TIMEOUT:-2400}"
PASS_TIMEOUT_OVERRIDE="${PASS_TIMEOUT_OVERRIDE:-true}"
PASS_ENDPOINT_OVERRIDES="${PASS_ENDPOINT_OVERRIDES:-true}"

TIMEOUT="${TIMEOUT:-${DEFAULT_TIMEOUT}}"
BASE_URL="${BASE_URL:-${OPENAI_BASE_URL:-}}"
API_KEY="${API_KEY:-${OPENAI_API_KEY:-}}"

mkdir -p "${OUTPUT_DIR}"

CMD=(
  "${PYTHON_BIN}" -m cuarewardbench.cli.eval_benchmark
  --model_config "${MODEL_CONFIG}"
  --eval_mode "${EVAL_MODE}"
  --num_workers "${NUM_WORKERS}"
  --num_items "${NUM_ITEMS}"
  --img_scale "${IMG_SCALE}"
  --max_screenshots "${MAX_SCREENSHOTS}"
  --output_dir "${OUTPUT_DIR}"
  --annotation_file "${ANNOTATION_FILE}"
  --trajectory_root "${TRAJECTORY_ROOT}"
  --prompt_dir "${PROMPT_DIR}"
)

if [[ -n "${EXP_SUFFIX}" ]]; then
  CMD+=(--exp_suffix "${EXP_SUFFIX}")
fi

if [[ "${ONLY_METRIC}" == "true" ]]; then
  CMD+=(--only_metric)
fi

if [[ "${PASS_TIMEOUT_OVERRIDE}" == "true" && -n "${TIMEOUT}" ]]; then
  CMD+=(--timeout "${TIMEOUT}")
fi

if [[ "${PASS_ENDPOINT_OVERRIDES}" == "true" ]]; then
  if [[ -n "${BASE_URL}" ]]; then
    CMD+=(--base_url "${BASE_URL}")
  fi
  if [[ -n "${API_KEY}" ]]; then
    CMD+=(--api_key "${API_KEY}")
  fi
fi

echo "=========================================="
echo "${RUN_TITLE}"
echo "=========================================="
echo "Model config:    ${MODEL_CONFIG}"
echo "Eval mode:       ${EVAL_MODE}"
echo "Num workers:     ${NUM_WORKERS}"
echo "Num items:       ${NUM_ITEMS} (0=all)"
echo "Max screenshots: ${MAX_SCREENSHOTS}"
echo "Trajectory root: ${TRAJECTORY_ROOT}"
echo "Output dir:      ${OUTPUT_DIR}"
echo "Exp suffix:      ${EXP_SUFFIX:-<none>}"
echo "Only metric:     ${ONLY_METRIC}"
echo "Timeout override: $([[ "${PASS_TIMEOUT_OVERRIDE}" == "true" && -n "${TIMEOUT}" ]] && echo set || echo unset)"
echo "Endpoint override: $([[ "${PASS_ENDPOINT_OVERRIDES}" == "true" && -n "${BASE_URL}" ]] && echo set || echo unset)"
echo "API key override: $([[ "${PASS_ENDPOINT_OVERRIDES}" == "true" && -n "${API_KEY}" ]] && echo set || echo unset)"
echo "=========================================="
echo ""
echo "Running: ${CMD[*]}"
echo ""

"${CMD[@]}"
