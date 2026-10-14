#!/usr/bin/env bash
# Final, H0-comparable evaluation for the GEPA × Terminal-Bench 2.0 unit.
#
# Installs a candidate instruction prompt into this unit's run entry, runs the frozen
# train split (30 tasks × 2 attempts, concurrency 10, local Docker) exactly like the
# H0 unit did, then restores the pristine H0 prompt and writes the summary.
#
# Usage: bash run_final_eval.sh <prompt_file> <run-name>
#   <prompt_file>  best prompt produced by run_gepa_tb2.py (e.g. runs/<run-id>/best_prompt.txt)
#   <run-name>     harbor job name, e.g. gepa-tb2-final-20261014
#
# Cost note: 30 tasks × 2 attempts ≈ $9.5 (measured on the identical H0 run, 2026-10-13).

set -euo pipefail

UNIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_ENTRY="$UNIT_DIR/code"
PROMPT_TEMPLATE="$RUN_ENTRY/prompt-templates/terminus-kira.txt"
H0_BACKUP="$UNIT_DIR/runs/terminus-kira.h0.txt"
H0_PROMPT_SHA256="adf2d40a4503965b307d348447f95141aa77db665c6571f3ab9512151894e6f6"

PROMPT_FILE="${1:?Usage: $0 <prompt_file> <run-name>}"
RUN_NAME="${2:?Usage: $0 <prompt_file> <run-name>}"
[[ -f "$PROMPT_FILE" ]] || { echo "prompt file not found: $PROMPT_FILE" >&2; exit 1; }

# 1. Make sure the pristine H0 prompt is backed up and verify it.
mkdir -p "$UNIT_DIR/runs"
if [[ ! -f "$H0_BACKUP" ]]; then
    current_sha="$(sha256sum "$PROMPT_TEMPLATE" | cut -d' ' -f1)"
    if [[ "$current_sha" != "$H0_PROMPT_SHA256" ]]; then
        echo "run entry prompt is not the recorded H0 prompt ($current_sha); refusing to proceed" >&2
        exit 1
    fi
    cp -p "$PROMPT_TEMPLATE" "$H0_BACKUP"
fi
[[ "$(sha256sum "$H0_BACKUP" | cut -d' ' -f1)" == "$H0_PROMPT_SHA256" ]] \
    || { echo "H0 prompt backup is corrupted" >&2; exit 1; }

# 2. Install the candidate prompt (restored on exit, whatever happens).
restore() { cp -p "$H0_BACKUP" "$PROMPT_TEMPLATE"; echo "restored H0 prompt"; }
trap restore EXIT
cp -p "$PROMPT_FILE" "$PROMPT_TEMPLATE"
echo "candidate prompt: $PROMPT_FILE (sha256 $(sha256sum "$PROMPT_FILE" | cut -d' ' -f1))"

# 3. Run the frozen train split, same protocol as the H0 unit.
cd "$RUN_ENTRY"
export HARBOR_MODEL="deepseek/deepseek-v4-flash"
export HARBOR_ENVIRONMENT=docker
export HARBOR_DATASET_PATH=/data1/users/zhaoXY/benchmarks/tb2-split-v1/train
bash scripts/run_eval.sh agents.baseline_kira:AgentHarness full 2 10 \
    --job-name "$RUN_NAME" --jobs-dir "$UNIT_DIR/runs/jobs" -y

# 4. Summarize (trap restores the prompt afterwards).
cd "$UNIT_DIR"
python3 summarize.py --job-dir "$UNIT_DIR/runs/jobs/$RUN_NAME"
