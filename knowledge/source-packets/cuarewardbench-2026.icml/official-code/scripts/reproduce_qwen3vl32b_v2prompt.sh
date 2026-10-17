#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Reproduce the historical metric file:
# crm_results/metrics_evalmode_sewsm_thinking_cuarewardbench-v0.4_Qwen3-VL-32B-Thinking_v2prompt.json
# Inferred from the filename and data_engine/eval_traj defaults:
# - eval_mode: sewsm_thinking
# - prompt: osworld_sewsm_thinking.json
# - model_config: qwen3vl32b_thinking_tione_config -> Qwen3-VL-32B-Thinking
# - max_screenshots: 20 (default; filename has no _maxS*)
# - exp_suffix: v2prompt

export RUN_TITLE="${RUN_TITLE:-CUARewardBench Historical v2prompt Reproduction}"
export OUTPUT_DIR="${OUTPUT_DIR:-${REPO_ROOT}/outputs/reproduce_qwen3vl32b_v2prompt}"
export TRAJECTORY_ROOT="${TRAJECTORY_ROOT:-${REPO_ROOT}/data/trajectories/osworld_verified}"
export MODEL_CONFIG="${MODEL_CONFIG:-qwen3vl32b_thinking_tione_config}"
export EVAL_MODE="${EVAL_MODE:-sewsm_thinking}"
export NUM_WORKERS="${NUM_WORKERS:-8}"
export NUM_ITEMS="${NUM_ITEMS:-0}"
export IMG_SCALE="${IMG_SCALE:-1.0}"
export MAX_SCREENSHOTS="${MAX_SCREENSHOTS:-20}"
export EXP_SUFFIX="${EXP_SUFFIX:-v2prompt}"
export PASS_TIMEOUT_OVERRIDE="${PASS_TIMEOUT_OVERRIDE:-false}"
export PASS_ENDPOINT_OVERRIDES="${PASS_ENDPOINT_OVERRIDES:-false}"
export DEFAULT_TIMEOUT="${DEFAULT_TIMEOUT:-}"

exec bash "${SCRIPT_DIR}/reproduce_qwen3vl32b_final.sh" "$@"
