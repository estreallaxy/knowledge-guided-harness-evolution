#!/usr/bin/env bash
# Usage: scripts/run_eval.sh <agent_import_path> [hard|full] [runs] [n_concurrent] [extra_harbor_flags...]

set -euo pipefail

AGENT_IMPORT_PATH="${1:?Usage: $0 <agent_import_path> [task_set] [runs] [n_concurrent] [extra_harbor_flags...]}"
TASK_SET="${2:-full}"
RUNS="${3:-2}"
N_CONCURRENT="${4:-50}"
shift "$(( $# < 4 ? $# : 4 ))"
EXTRA_FLAGS=("$@")

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
export PYTHONPATH="$REPO_DIR${PYTHONPATH:+:$PYTHONPATH}"

# Load local .env (override shell environment)
if [[ -f "$REPO_DIR/.env" ]]; then
    set -a
    # shellcheck source=/dev/null
    source "$REPO_DIR/.env"
    set +a
fi

# 适配记录（王懿，2026-10-07）：
#   上游默认是 anthropic/claude-opus-4-6 + runloop 云沙箱（需 RUNLOOP_API_KEY）。
#   本机改为 deepseek/deepseek-flash + 本地 Docker（Harbor 自身的默认环境），
#   端点与密钥只从环境变量读取。详见 ../../../notes/environment.md
MODEL="${HARBOR_MODEL:-deepseek/deepseek-flash}"
HARBOR_TIMEOUT_SECONDS="${HARBOR_TIMEOUT_SECONDS:-28800}"
HARBOR_ENVIRONMENT="${HARBOR_ENVIRONMENT:-docker}"
HARBOR_API_BASE="${HARBOR_API_BASE:-https://api.deepseek.com/v1}"

case "$HARBOR_ENVIRONMENT" in
    docker|runloop|modal) ;;
    *) echo "Unknown HARBOR_ENVIRONMENT '$HARBOR_ENVIRONMENT'. Use: docker | runloop | modal" >&2; exit 1 ;;
esac

# litellm 未登记 deepseek-flash，显式提供上下文档位，避免误判上下文长度。
MODEL_INFO_JSON='{"max_input_tokens":1048576,"max_output_tokens":393216}'

# 数据集来源（王懿，2026-10-08）：默认走上游 registry 的 terminal-bench@2.0（89 题全量）。
# 设置 HARBOR_DATASET_PATH 时改用本地固定划分目录（Harbor `-p`），
# 例如 /data1/users/wangY/benchmarks/tb2-split-v1/train。
HARBOR_DATASET_PATH="${HARBOR_DATASET_PATH:-}"
HARBOR_DATASET="${HARBOR_DATASET:-terminal-bench@2.0}"

uv run python "$REPO_DIR/meta_harness.py" --validate-agent "$AGENT_IMPORT_PATH"

# 30-task hard subset for cheaper development and debugging loops.
HARD_TASKS=(
    bn-fit-modify cancel-async-tasks circuit-fibsqrt configure-git-webserver
    dna-assembly extract-moves-from-video feal-differential-cryptanalysis
    feal-linear-cryptanalysis fix-code-vulnerability fix-ocaml-gc
    gpt2-codegolf install-windows-3.11 llm-inference-batching-scheduler
    make-doom-for-mips make-mips-interpreter mcmc-sampling-stan
    model-extraction-relu-logits password-recovery path-tracing
    path-tracing-reverse polyglot-rust-c protein-assembly regex-chess
    sam-cell-seg sparql-university torch-pipeline-parallelism
    torch-tensor-parallelism train-fasttext video-processing write-compressor
)

TASK_FLAGS=()
case "$TASK_SET" in
    hard)
        for t in "${HARD_TASKS[@]}"; do TASK_FLAGS+=(-i "$t"); done ;;
    full)
        ;;  # no task flags: harbor runs the full dataset
    *)
        echo "Unknown task_set '$TASK_SET'. Use: hard | full" >&2; exit 1 ;;
esac

echo "agent:       $AGENT_IMPORT_PATH"
echo "environment: $HARBOR_ENVIRONMENT"
echo "task_set:    $TASK_SET"
echo "dataset:     ${HARBOR_DATASET_PATH:-$HARBOR_DATASET}"
echo "model:       $MODEL"
echo "api_base:    ${HARBOR_API_BASE:-<provider default>}"
echo "concurrent:  $N_CONCURRENT"
echo "runs:        $RUNS"
echo "timeout:     ${HARBOR_TIMEOUT_SECONDS}s"
echo ""

TIMEOUT_CMD=()
if [[ "${HARBOR_EXTERNAL_TIMEOUT:-0}" != "1" ]]; then
    if command -v timeout >/dev/null 2>&1; then
        TIMEOUT_CMD=(timeout --signal=TERM --kill-after=60 "$HARBOR_TIMEOUT_SECONDS")
    elif command -v gtimeout >/dev/null 2>&1; then
        TIMEOUT_CMD=(gtimeout --signal=TERM --kill-after=60 "$HARBOR_TIMEOUT_SECONDS")
    fi
fi

CMD=(
    uv run harbor run
    --agent "$AGENT_IMPORT_PATH"
    -m "$MODEL"
    -e "$HARBOR_ENVIRONMENT"
    -n "$N_CONCURRENT"
    --n-attempts "$RUNS"
    --ak temperature=0.7
)
if [[ -n "$HARBOR_DATASET_PATH" ]]; then
    CMD+=(-p "$HARBOR_DATASET_PATH")
else
    CMD+=(-d "$HARBOR_DATASET")
fi
# 仅在使用非 Anthropic 兼容的 OpenAI 端点时透传 api_base 与 model_info。
if [[ -n "$HARBOR_API_BASE" ]]; then
    CMD+=(--ak "api_base=$HARBOR_API_BASE" --ak "model_info=$MODEL_INFO_JSON")
fi
if [[ ${#TASK_FLAGS[@]} -gt 0 ]]; then
    CMD+=("${TASK_FLAGS[@]}")
fi
if [[ ${#EXTRA_FLAGS[@]} -gt 0 ]]; then
    CMD+=("${EXTRA_FLAGS[@]}")
fi

if [[ ${#TIMEOUT_CMD[@]} -gt 0 ]]; then
    "${TIMEOUT_CMD[@]}" "${CMD[@]}"
else
    "${CMD[@]}"
fi
