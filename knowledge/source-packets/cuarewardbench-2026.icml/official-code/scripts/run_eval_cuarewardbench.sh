#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# =============================================================================
# CUARewardBench 评估脚本
# 用于测试改善后的评估链路（prompt优化、parser改善、repetition_penalty等）
# 在 cuarewardbench 基准上的得分，对比改善前是否退步。
#
# 底层共享：与 run_eval_trajectories.sh 使用相同的：
#   - LLMEvaluator (llm_eval.py)
#   - prompt 文件 (osworld_sewsm_thinking.json)
#   - model_config (qwen3vl32b_thinking_tione_config: repetition_penalty=1.05, max_tokens=16384)
#   - result_parser (parse_from_response_sewsm)
#
# 使用方法: bash run_eval_cuarewardbench.sh
# =============================================================================

export RUN_TITLE="${RUN_TITLE:-CUARewardBench Evaluation}"
export MODEL_CONFIG="${MODEL_CONFIG:-qwen3vl32b_thinking_tione_config}"
# export MODEL_CONFIG="${MODEL_CONFIG:-kimi_k25_tione_config}"
# export MODEL_CONFIG="${MODEL_CONFIG:-qwen35_tione_config}"

export EVAL_MODE="${EVAL_MODE:-sewsm_thinking}"
export NUM_WORKERS="${NUM_WORKERS:-8}"
export NUM_ITEMS="${NUM_ITEMS:-0}"
export IMG_SCALE="${IMG_SCALE:-1.0}"
export MAX_SCREENSHOTS="${MAX_SCREENSHOTS:-20}"
export EXP_SUFFIX="${EXP_SUFFIX:-}"
export OUTPUT_DIR="${OUTPUT_DIR:-${REPO_ROOT}/outputs/crm_results}"
export TRAJECTORY_ROOT="${TRAJECTORY_ROOT:-${REPO_ROOT}/data/trajectories/osworld_verified}"
export ONLY_METRIC="${ONLY_METRIC:-false}"
export PASS_TIMEOUT_OVERRIDE="${PASS_TIMEOUT_OVERRIDE:-false}"
export PASS_ENDPOINT_OVERRIDES="${PASS_ENDPOINT_OVERRIDES:-true}"

exec bash "${SCRIPT_DIR}/reproduce_qwen3vl32b_final.sh" "$@"
