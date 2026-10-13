#!/usr/bin/env bash
# 本地 docker 后端的一键入口（周梦凡个人适配，记录于 notes/adaptations.md）。
#
# 为什么不把这些设置写进 .env：run_eval.sh 的 dotenv 段会覆盖 shell 环境，
# 而 tests/test_meta_harness.py 断言默认后端为 runloop，写进 .env 会让那两条测试失败。
#
# 用法: code-adaptation/scripts/run_local_docker.sh <agent_import_path> [hard|full] [runs] [n_concurrent] [extra harbor flags...]
# 例:   code-adaptation/scripts/run_local_docker.sh agents.baseline_kira:AgentHarness full 1 1 -i extract-elf
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RD="$(cd "$SCRIPT_DIR/../../.." && pwd)/code/reference_examples/terminal_bench_2"
# `uv run` 按当前目录找 pyproject.toml，不切到 runner 目录会落到别的环境上
# （表现为 ModuleNotFoundError: No module named 'dotenv'）。
cd "$RD"

AGENT="${1:?用法: $0 <agent_import_path> [hard|full] [runs] [n_concurrent] [extra harbor flags...]}"
TASK_SET="${2:-hard}"     # 本地 docker 默认先跑便宜的 30 题 hard 子集
RUNS="${3:-2}"
CONCURRENT="${4:-4}"      # 参考实现默认 50 并发，本地 docker 必须显著降低
shift "$(( $# < 4 ? $# : 4 ))"
EXTRA=("$@")

export HARBOR_ENVIRONMENT="${HARBOR_ENVIRONMENT:-docker}"
export HARBOR_MODEL="${HARBOR_MODEL:-deepseek/deepseek-v4-flash}"
# 仅在变量"未设置"时给默认值；显式置空（HARBOR_TASK_PATH=）表示回落到 -d，
# 便于直接跑 smoke task（extract-elf 不在 train 划分里）。
if [ -z "${HARBOR_TASK_PATH+set}" ]; then
  HARBOR_TASK_PATH=/data1/users/zhouMF/benchmarks/tb2-split-v1/train
fi
export HARBOR_TASK_PATH

if [ -n "$HARBOR_TASK_PATH" ] && [ ! -d "$HARBOR_TASK_PATH" ]; then
  echo "!! 本地任务集目录不存在: $HARBOR_TASK_PATH" >&2
  echo "   在仓库根先生成：" >&2
  echo "     python3 benchmarks/terminal-bench-2.0/prepare_dataset.py \\" >&2
  echo "       --source benchmarks/terminal-bench-2.0/dataset \\" >&2
  echo "       --output /data1/users/zhouMF/benchmarks/tb2-split-v1" >&2
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "!! 无法连接 Docker 守护进程，请先确认 docker 可用。" >&2
  exit 1
fi

echo "==> 后端=$HARBOR_ENVIRONMENT 模型=$HARBOR_MODEL 并发=$CONCURRENT 任务集=$HARBOR_TASK_PATH"
exec "$RD/scripts/run_eval.sh" "$AGENT" "$TASK_SET" "$RUNS" "$CONCURRENT" ${EXTRA[@]+"${EXTRA[@]}"}
