#!/usr/bin/env bash
# Claude Code → deepseek 的本地 Anthropic 兼容网关（周梦凡个人工具）。
#
# 背景：上游 meta_harness.py 的提议器（propose_claude）用 subprocess 调 `claude -p`，
# 走的是 Claude Code 的 Anthropic 接口。本机没有 Claude Code 订阅，共同协议又把优化模型
# 固定为 deepseek-v4-flash，所以这里用 litellm 代理把 Anthropic /v1/messages 映射到
# deepseek。这只换"模型从哪来"，不动 claude_wrapper.py 与提议器代码路径。
#
# 用法:
#   code-adaptation/scripts/claude_deepseek_gateway.sh start|stop|status
#
# 启动后需要让 claude 指向本网关（提议器运行环境里要有这两条）：
#   export ANTHROPIC_BASE_URL=http://127.0.0.1:4000
#   export ANTHROPIC_AUTH_TOKEN=sk-local-proxy
# 不要设 ANTHROPIC_API_KEY：propose_claude() 会把它 pop 掉。
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNNER_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)/code/reference_examples/terminal_bench_2"
PROXY_HOME="${PROXY_HOME:-$HOME/.local/litellm-proxy}"
PROXY_BIN="$PROXY_HOME/bin/litellm"
PROXY_CONFIG="$PROXY_HOME/config.yaml"
PROXY_LOG="$PROXY_HOME/proxy.log"
NODE_BIN_DIR="${NODE_BIN_DIR:-$HOME/.local/node22/bin}"
HOST=127.0.0.1
PORT="${GATEWAY_PORT:-4000}"

case "${1:-status}" in
  start)
    if [ ! -x "$PROXY_BIN" ]; then
      echo "缺少 litellm 代理环境: $PROXY_BIN" >&2
      echo "安装：uv venv $PROXY_HOME --python 3.12 && uv pip install --python $PROXY_HOME/bin/python 'litellm[proxy]'" >&2
      exit 1
    fi
    if timeout 5 curl -sS -o /dev/null "http://$HOST:$PORT/health/liveliness" 2>/dev/null; then
      echo "网关已在运行: http://$HOST:$PORT"
      exit 0
    fi
    # 凭据来自 runner 目录的 .env（只读，不入库）
    set -a
    # shellcheck source=/dev/null
    . "$RUNNER_DIR/.env"
    set +a
    if [ -z "${DEEPSEEK_API_KEY:-}" ]; then
      echo "!! $RUNNER_DIR/.env 里的 DEEPSEEK_API_KEY 为空" >&2
      exit 1
    fi
    export PATH="$NODE_BIN_DIR:$PATH"
    setsid nohup "$PROXY_BIN" --config "$PROXY_CONFIG" --host "$HOST" --port "$PORT" \
      > "$PROXY_LOG" 2>&1 < /dev/null &
    for _ in $(seq 1 40); do
      sleep 2
      if timeout 5 curl -sS -o /dev/null "http://$HOST:$PORT/health/liveliness" 2>/dev/null; then
        echo "网关已启动: http://$HOST:$PORT（日志 $PROXY_LOG）"
        exit 0
      fi
    done
    echo "!! 网关启动超时，看 $PROXY_LOG" >&2
    exit 1
    ;;
  stop)
    pkill -f "litellm --config $PROXY_CONFIG" 2>/dev/null && echo "已停止" || echo "没有在跑的网关"
    ;;
  status)
    if timeout 5 curl -sS -o /dev/null "http://$HOST:$PORT/health/liveliness" 2>/dev/null; then
      echo "运行中: http://$HOST:$PORT"
    else
      echo "未运行"
      exit 1
    fi
    ;;
  *)
    echo "用法: $0 start|stop|status" >&2
    exit 2
    ;;
esac
