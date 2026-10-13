#!/usr/bin/env bash
# 守护 P3 重跑：日志里出现 Insufficient Balance 就立刻熔断，避免整轮废弃。
# 用法：bash code-adaptation/scripts/h0_baseline_watch.sh （job 结束后自动追加汇总到 notes/run-log.md）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS="$(cd "$SCRIPT_DIR/../.." && pwd)"                                    # .../meta-harness/terminal-bench-2.0
RD="$(cd "$WS/.." && pwd)/code/reference_examples/terminal_bench_2"
LOG=$WS/runs/h0-baseline-r2.log
while pgrep -f "harbor run --agent agents.baseline_kira" >/dev/null 2>&1; do
  if grep -q "Insufficient Balance" "$LOG" 2>/dev/null; then
    echo "!! 检测到 Insufficient Balance $(date -Is)" >> "$WS/runs/h0-r2-watch.log"
    pkill -f "harbor run --agent agents.baseline_kira"
    pkill -f "scripts/run_eval.sh"
    echo "BALANCE_STOP $(date -Is)" > "$WS/runs/h0-r2.done"
    exit 0
  fi
  sleep 60
done
echo "job 进程退出: $(date -Is)" >> "$WS/runs/h0-r2-watch.log"
python3 "$SCRIPT_DIR/summarize_run.py" \
  "$RD/jobs/h0-baseline-r2" \
  --append-to "$WS/notes/run-log.md" >> "$WS/runs/h0-r2-watch.log" 2>&1
echo "DONE $(date -Is)" > "$WS/runs/h0-r2.done"
