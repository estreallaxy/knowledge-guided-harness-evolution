#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

usage() {
  cat <<'USAGE'
Evaluate newly generated agent trajectory directories with a reward model.

Single trial:
  TRAJ_DIR=/path/to/trial_1 bash scripts/run_eval_trajectories.sh

Multiple explicit trials, merged into one worker pool:
  TRAJ_DIRS=/path/to/trial_1,/path/to/trial_2 bash scripts/run_eval_trajectories.sh

Generate multi-trial dirs from a base directory and prefix:
  BASE_DIR=/path/to/runs \
  TRIAL_PREFIX=tke_browser_trial \
  TRIAL_RANGE=1-3,5 \
  bash scripts/run_eval_trajectories.sh

Environment variables:
  MODEL_CONFIG      Model registry key. Default: qwen3vl32b_thinking_tione_config
  EVAL_MODE         Evaluation mode. Default: sewsm_thinking
  NUM_WORKERS       Parallel workers. Default: 8
  NUM_ITEMS         Max trajectories to evaluate; 0 means all. Default: 0
  IMG_SCALE         Image scale factor. Default: 1.0
  MAX_SCREENSHOTS   Max action screenshots per trajectory; 0 means all. Default: 34
  PROMPT_DIR        Prompt directory. Default: configs/prompts
  PROMPT_FILE       Optional prompt file override.
  BASE_URL          Optional OpenAI-compatible endpoint override. Also reads OPENAI_BASE_URL.
  API_KEY           Optional API key override. Also reads OPENAI_API_KEY.
  TIMEOUT           Optional request timeout in seconds.
USAGE
}

generate_traj_dirs() {
  local base_dir=$1
  local prefix=$2
  local range=$3
  local dirs=()

  IFS=',' read -ra parts <<< "${range}"
  for part in "${parts[@]}"; do
    if [[ "${part}" =~ ^([0-9]+)-([0-9]+)$ ]]; then
      for i in $(seq "${BASH_REMATCH[1]}" "${BASH_REMATCH[2]}"); do
        dirs+=("${base_dir}/${prefix}_${i}")
      done
    elif [[ "${part}" =~ ^[0-9]+$ ]]; then
      dirs+=("${base_dir}/${prefix}_${part}")
    else
      echo "[ERROR] Invalid TRIAL_RANGE part: ${part}" >&2
      exit 2
    fi
  done

  local result
  result=$(IFS=','; echo "${dirs[*]}")
  echo "${result}"
}

PYTHON_BIN="${PYTHON_BIN:-python3}"
MODEL_CONFIG="${MODEL_CONFIG:-qwen3vl32b_thinking_tione_config}"
EVAL_MODE="${EVAL_MODE:-sewsm_thinking}"
NUM_WORKERS="${NUM_WORKERS:-8}"
NUM_ITEMS="${NUM_ITEMS:-0}"
IMG_SCALE="${IMG_SCALE:-1.0}"
MAX_SCREENSHOTS="${MAX_SCREENSHOTS:-34}"
PROMPT_DIR="${PROMPT_DIR:-${REPO_ROOT}/configs/prompts}"
PROMPT_FILE="${PROMPT_FILE:-}"
BASE_URL="${BASE_URL:-${OPENAI_BASE_URL:-}}"
API_KEY="${API_KEY:-${OPENAI_API_KEY:-}}"
TIMEOUT="${TIMEOUT:-}"

TRAJ_DIR="${TRAJ_DIR:-}"
TRAJ_DIRS="${TRAJ_DIRS:-}"
BASE_DIR="${BASE_DIR:-}"
TRIAL_PREFIX="${TRIAL_PREFIX:-}"
TRIAL_RANGE="${TRIAL_RANGE:-1}"

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

cmd=("${PYTHON_BIN}" -m cuarewardbench.cli.eval_trajectory)
mode_label=""

if [[ -n "${TRAJ_DIRS}" ]]; then
  cmd+=(--traj_dirs "${TRAJ_DIRS}")
  mode_label="explicit multi-trial merged"
elif [[ -n "${TRAJ_DIR}" ]]; then
  cmd+=(--traj_dir "${TRAJ_DIR}")
  mode_label="single trial"
elif [[ -n "${BASE_DIR}" && -n "${TRIAL_PREFIX}" ]]; then
  TRAJ_DIRS="$(generate_traj_dirs "${BASE_DIR}" "${TRIAL_PREFIX}" "${TRIAL_RANGE}")"
  cmd+=(--traj_dirs "${TRAJ_DIRS}")
  mode_label="generated multi-trial merged"
else
  usage >&2
  echo "[ERROR] Set one of TRAJ_DIR, TRAJ_DIRS, or BASE_DIR+TRIAL_PREFIX." >&2
  exit 2
fi

cmd+=(
  --model_config "${MODEL_CONFIG}"
  --eval_mode "${EVAL_MODE}"
  --num_workers "${NUM_WORKERS}"
  --num_items "${NUM_ITEMS}"
  --img_scale "${IMG_SCALE}"
  --max_screenshots "${MAX_SCREENSHOTS}"
  --prompt_dir "${PROMPT_DIR}"
  --skip_existing
)

if [[ -n "${PROMPT_FILE}" ]]; then
  cmd+=(--prompt_file "${PROMPT_FILE}")
fi
if [[ -n "${BASE_URL}" ]]; then
  cmd+=(--base_url "${BASE_URL}")
fi
if [[ -n "${API_KEY}" ]]; then
  cmd+=(--api_key "${API_KEY}")
fi
if [[ -n "${TIMEOUT}" ]]; then
  cmd+=(--timeout "${TIMEOUT}")
fi

echo "=========================================="
echo "Trajectory Evaluation"
echo "=========================================="
echo "Mode: ${mode_label}"
if [[ -n "${TRAJ_DIR}" ]]; then echo "Trajectory dir: ${TRAJ_DIR}"; fi
if [[ -n "${TRAJ_DIRS}" ]]; then echo "Trajectory dirs: ${TRAJ_DIRS}"; fi
if [[ -n "${BASE_DIR}" ]]; then echo "Base dir: ${BASE_DIR}"; fi
if [[ -n "${TRIAL_PREFIX}" ]]; then echo "Trial prefix: ${TRIAL_PREFIX}"; fi
echo "Trial range: ${TRIAL_RANGE}"
echo "Model config: ${MODEL_CONFIG}"
echo "Eval mode: ${EVAL_MODE}"
echo "Num workers: ${NUM_WORKERS}"
echo "Max screenshots: ${MAX_SCREENSHOTS}"
echo "Prompt dir: ${PROMPT_DIR}"
echo "Base URL override: $([[ -n "${BASE_URL}" ]] && echo set || echo unset)"
echo "API key override: $([[ -n "${API_KEY}" ]] && echo set || echo unset)"
echo "=========================================="

"${cmd[@]}"

echo "=========================================="
echo "Trajectory evaluation completed."
echo "=========================================="
