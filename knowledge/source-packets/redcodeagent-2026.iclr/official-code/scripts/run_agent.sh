#!/usr/bin/env bash
# ==============================================================================
# RedCodeAgent - Agent runner
# ------------------------------------------------------------------------------
# Unified entry point: invokes redcodeagent/run_agent.py to run the red-teaming
# Agent evaluation against the given dataset / target Agent.
#
# Usage:
#   bash scripts/run_agent.sh                          # use defaults below
#   bash scripts/run_agent.sh RedCode-Exec OCI 1 1
#       └ dataset      └ target └ start_idx └ end_idx
#
# Optional environment variables:
#   CUDA_VISIBLE_DEVICES   # GPU id, default 0
#   LOG_DIR                # log directory, default ./logs
#   TAG                    # run tag (maps to --baseline), default Agent
#   TOPK                   # number of memory entries retrieved, default 3
#   MEM                    # whether to use memory (True/False), default True
#
# Supported datasets: RedCode-Exec / RedCode-Gen / RMC /
#                     RedCode-C / RedCode-CPP / RedCode-Java
# Supported targets:  OCI / RA (More agents coming soon)
# ==============================================================================

set -euo pipefail

# ---------- Paths ----------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PKG_DIR="${REPO_ROOT}/redcodeagent"

# ---------- Arguments ----------
DATASET="${1:-RedCode-Exec}"
TARGET_MODEL="${2:-OCI}"
START_INDEX="${3:-1}"
END_INDEX="${4:-1}"

# ---------- Configurable environment variables ----------
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"
LOG_DIR="${LOG_DIR:-${REPO_ROOT}/logs}"
TAG="${TAG:-Agent}" # run RedCodeAgent
TOPK="${TOPK:-3}"
MEM="${MEM:-True}"

# ---------- API keys ----------
# Priority: external shell env var > value hardcoded here > config file.
export OPENAI_API_KEY=""

# HuggingFace token — needed when the AmpleGCG jailbreak tool actually
# runs (it pulls the gated AmpleGCG weights from the HF Hub). Paste your token
# between the quotes, or export HF_TOKEN in your outer shell before running.
export HF_TOKEN=""
export HUGGINGFACEHUB_API_TOKEN="${HUGGINGFACEHUB_API_TOKEN:-${HF_TOKEN}}"

mkdir -p "${LOG_DIR}"

STAMP="$(date +%Y%m%d_%H%M%S)"
LOG_FILE="${LOG_DIR}/${TARGET_MODEL}_${TAG}_${DATASET}_${START_INDEX}-${END_INDEX}_${STAMP}.log"

echo "==============================================="
echo "  RedCodeAgent run"
echo "-----------------------------------------------"
echo "  tag          : ${TAG}"
echo "  dataset      : ${DATASET}"
echo "  target_model : ${TARGET_MODEL}"
echo "  index range  : ${START_INDEX} - ${END_INDEX}"
echo "  topk         : ${TOPK}"
echo "  mem          : ${MEM}"
echo "  CUDA         : ${CUDA_VISIBLE_DEVICES}"
echo "  log          : ${LOG_FILE}"
echo "==============================================="

cd "${PKG_DIR}"

python -u run_agent.py \
    --baseline     "${TAG}" \
    --dataset      "${DATASET}" \
    --target_model "${TARGET_MODEL}" \
    --start_index  "${START_INDEX}" \
    --end_index    "${END_INDEX}" \
    --topk         "${TOPK}" \
    --mem          "${MEM}" \
    > "${LOG_FILE}" 2>&1 &

RUN_PID=$!
echo "started pid=${RUN_PID}"
echo "tail -f ${LOG_FILE}"
