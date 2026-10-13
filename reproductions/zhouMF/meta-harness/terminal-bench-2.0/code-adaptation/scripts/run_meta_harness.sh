#!/usr/bin/env bash
# Meta-Harness 优化循环入口（周梦凡个人适配，记录于 notes/adaptations.md）。
#
# 用法:
#   code-adaptation/scripts/run_meta_harness.sh <run_name> [额外 meta_harness.py 参数...]
# 例（P5 冒烟）:
#   code-adaptation/scripts/run_meta_harness.sh p5-smoke --iterations 1 --trials 1 --skip-baseline --concurrent 2
# 例（P6 正式）:
#   code-adaptation/scripts/run_meta_harness.sh p6-main --iterations 5 --trials 2 --concurrent 8 --full-eval
#
# 循环内每轮评测走 runner 的 scripts/run_eval.sh，任务范围由 HARBOR_TASK_PATH 决定，因此固定在 train。
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS="$(cd "$SCRIPT_DIR/../.." && pwd)"                          # reproductions/zhouMF/meta-harness/terminal-bench-2.0
RD="$(cd "$WS/.." && pwd)/code/reference_examples/terminal_bench_2"

RUN_NAME="${1:?用法: $0 <run_name> [meta_harness.py 参数...]}"
shift

export PATH="$HOME/.local/bin:$PATH"
export HARBOR_ENVIRONMENT="${HARBOR_ENVIRONMENT:-docker}"
export HARBOR_TASK_PATH="${HARBOR_TASK_PATH:-/data1/users/zhouMF/benchmarks/tb2-split-v1/train}"
export HARBOR_TIMEOUT_SECONDS="${HARBOR_TIMEOUT_SECONDS:-3600}"

# 优化模型（共同协议固定）与提议器落地方式：Claude Code CLI → 本地网关 → deepseek。
export META_HARNESS_MODEL="${META_HARNESS_MODEL:-deepseek/deepseek-v4-flash}"
export META_HARNESS_SMOKE_TASK="${META_HARNESS_SMOKE_TASK:-bn-fit-modify}"
export ANTHROPIC_BASE_URL="${ANTHROPIC_BASE_URL:-http://127.0.0.1:4000}"
export ANTHROPIC_AUTH_TOKEN="${ANTHROPIC_AUTH_TOKEN:-sk-local-proxy}"
export PATH="$HOME/.local/node22/bin:$PATH"
# 不设 ANTHROPIC_API_KEY：propose_claude() 会把它 pop 掉。

if ! timeout 5 curl -sS -o /dev/null "$ANTHROPIC_BASE_URL/health/liveliness"; then
  echo "!! 提议器网关未运行：$ANTHROPIC_BASE_URL" >&2
  echo "   先执行：$SCRIPT_DIR/claude_deepseek_gateway.sh start" >&2
  exit 1
fi

if [ ! -d "$HARBOR_TASK_PATH" ]; then
  echo "!! 本地任务集目录不存在: $HARBOR_TASK_PATH" >&2
  exit 1
fi

echo "==> run=$RUN_NAME model=$META_HARNESS_MODEL smoke_task=$META_HARNESS_SMOKE_TASK task_path=$HARBOR_TASK_PATH"
cd "$RD"
exec uv run python meta_harness.py --run-name "$RUN_NAME" "$@"
