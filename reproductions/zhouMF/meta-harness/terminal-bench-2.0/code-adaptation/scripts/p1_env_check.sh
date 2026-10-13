#!/usr/bin/env bash
# P1/P2 环境检查（周梦凡个人工具，不属于 code/ 上游副本）
#
# 在具备网络与 docker 的终端执行一次：
#   bash reproductions/zhouMF/meta-harness/terminal-bench-2.0/code-adaptation/scripts/p1_env_check.sh
#
# 全部证据同时打印并写入 notes/p1-env-report.txt，便于离线复核与交叉核对。
# 可选环境变量：
#   PULL_IMAGE=1     额外验证能否拉取一个 TB2 任务镜像（数百 MB）
#   SKIP_SYNC=1      跳过 uv sync
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(cd "$SCRIPT_DIR/../.." && pwd)"               # reproductions/zhouMF/meta-harness/terminal-bench-2.0
REPO_ROOT="$(cd "$WORKSPACE/../../../.." && pwd)"          # 仓库根
RUNNER_DIR="$(cd "$WORKSPACE/.." && pwd)/code/reference_examples/terminal_bench_2"
REPORT="$WORKSPACE/notes/p1-env-report.txt"
TASK_IMAGE="alexgshaw/extract-elf:20251031"

mkdir -p "$WORKSPACE/notes"
exec > >(tee "$REPORT") 2>&1

RESULTS=()
record() { RESULTS+=("$1|$2"); printf '\n[%-4s] %s\n' "$1" "$2"; }

section() { printf '\n\n======== %s ========\n' "$1"; }

section "0. 环境快照"
date -Is
echo "user=$(whoami)  host=$(hostname)"
uname -srm
echo "cpu=$(nproc)  mem=$(free -g | awk 'NR==2{print $2"G"}')"
echo "repo_root=$REPO_ROOT"
echo "runner_dir=$RUNNER_DIR"

section "1. 网络"
if timeout 15 curl -sSI https://github.com >/dev/null 2>&1; then
  record PASS "github.com 可达"
else
  record FAIL "github.com 不可达"
fi
if timeout 15 curl -sSI https://astral.sh >/dev/null 2>&1; then
  record PASS "astral.sh 可达"
else
  record FAIL "astral.sh 不可达（uv 安装会失败）"
fi

section "2. Docker"
if timeout 20 docker info >/dev/null 2>&1; then
  record PASS "docker 守护进程可用：$(docker version --format '{{.Server.Version}}' 2>/dev/null)"
  echo "data-root=$(docker info --format '{{.DockerRootDir}}' 2>/dev/null)"
  echo "storage=$(docker info --format '{{.Driver}}' 2>/dev/null)"
  if [ "${PULL_IMAGE:-0}" = "1" ]; then
    echo "拉取 $TASK_IMAGE ..."
    if timeout 900 docker pull "$TASK_IMAGE"; then
      record PASS "任务镜像可拉取"
    else
      record FAIL "任务镜像拉取失败"
    fi
  else
    echo "(跳过镜像拉取；设 PULL_IMAGE=1 可验证)"
  fi
else
  record FAIL "docker 守护进程不可用"
fi

section "3. uv"
if ! command -v uv >/dev/null 2>&1; then
  echo "未找到 uv，尝试安装到 \$HOME/.local/bin ..."
  if timeout 120 curl -LsSf https://astral.sh/uv/install.sh | sh; then
    record PASS "uv 安装完成"
  else
    record FAIL "uv 安装失败"
  fi
fi
export PATH="$HOME/.local/bin:$PATH"
if command -v uv >/dev/null 2>&1; then
  record PASS "uv $(uv --version 2>&1)"
else
  record FAIL "uv 仍不可用，后续步骤会失败"
fi

section "4. uv sync"
if [ "${SKIP_SYNC:-0}" = "1" ]; then
  record SKIP "按要求跳过 uv sync"
elif command -v uv >/dev/null 2>&1; then
  if (cd "$RUNNER_DIR" && timeout 1800 uv sync); then
    record PASS "uv sync 成功"
    echo "--- python ---"
    (cd "$RUNNER_DIR" && uv run python -V) 2>&1
  else
    record FAIL "uv sync 失败"
  fi
else
  record FAIL "无 uv，跳过 uv sync"
fi

section "5. Harbor 支持的后端（关键）"
if command -v uv >/dev/null 2>&1; then
  HELPTXT="$(cd "$RUNNER_DIR" && timeout 300 uv run harbor run --help 2>&1 || true)"
  # rich 会把后端长列表折行（docker 被拆成 "doc ker"、旁边还有 "dockbox"），
  # 所以先去空白与制表边框再匹配，避免误报。
  if printf '%s' "$HELPTXT" | python3 -c "import re,sys; sys.exit(0 if 'docker' in re.sub(r'[\s\u2502\u2500|]', '', sys.stdin.read()) else 1)"; then
    record PASS "harbor run --help 列出 docker 后端（-e docker 可用）"
  else
    record FAIL "harbor run --help 未列出 docker 后端"
  fi
  printf '%s\n' "$HELPTXT" | sed -n '1,14p'
else
  record FAIL "无 uv，无法查询 harbor"
fi

section "6. 免 provider 单测"
if command -v uv >/dev/null 2>&1; then
  if (cd "$RUNNER_DIR" && timeout 600 uv run python -m unittest -v \
        tests.test_meta_harness.AgentClassValidationTests 2>&1 | tail -25); then
    record PASS "AgentClassValidationTests"
  else
    record FAIL "AgentClassValidationTests"
  fi
  if (cd "$RUNNER_DIR" && timeout 600 uv run python -m unittest -v \
        tests.test_meta_harness.TimeoutWiringTests 2>&1 | tail -30); then
    record PASS "TimeoutWiringTests"
  else
    record FAIL "TimeoutWiringTests"
  fi
else
  record FAIL "无 uv，跳过单测"
fi

section "7. 凭据是否就位（只报是否存在，不打印取值）"
if [ -f "$RUNNER_DIR/.env" ]; then
  echo ".env 存在，检查变量是否非空："
  for v in DEEPSEEK_API_KEY DEEPSEEK_API_BASE OPENAI_API_KEY OPENAI_API_BASE; do
    val="$(grep -E "^${v}=" "$RUNNER_DIR/.env" 2>/dev/null | tail -1 | cut -d= -f2-)"
    if [ -n "$val" ]; then echo "  $v 已填（长度 ${#val}）"; else echo "  $v 空"; fi
  done
else
  echo ".env 不存在；需 cp .env.example .env 后填写。"
fi

section "结论汇总"
printf '%-6s %s\n' "结果" "检查项"
for row in "${RESULTS[@]}"; do printf '%-6s %s\n' "${row%%|*}" "${row#*|}"; done
printf '\n报告已写入: %s\n' "$REPORT"
