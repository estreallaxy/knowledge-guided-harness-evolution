# H0 × Terminal-Bench 2.0 复现记录（王懿，阶段一）

记录时间：2026-10-07 ~ 2026-10-09。本文件只覆盖 **H0 基线运行**；代码适配清单（改了什么上游代码、为什么、
如何验证）记录在 `reproductions/wangY/meta-harness/terminal-bench-2.0/notes/stage1-summary.md`，
两条线共用同一入口与同一套执行条件。凭据一律不入库，只登记变量名（`code/reference_examples/terminal_bench_2/.env.example`）。

## 1. 环境与准备

- 工作目录：`reproductions/wangY/meta-harness/code/reference_examples/terminal_bench_2/`；
  `uv sync` 安装 harbor 0.18.0 / litellm 1.84.10 / terminal-bench 0.2.18（PyPI，见适配清单 pyproject 条目）。
- 执行模型 `deepseek/deepseek-flash`（= 团队约定 deepseek-v4-flash，实测端点别名同模型），temperature 0.7，
  沙箱 `HARBOR_ENVIRONMENT=docker`（Harbor 本地沙箱，无需云密钥）。
- 数据集：按仓库 `benchmarks/terminal-bench-2.0/README.md` 在本人工作区生成独立划分目录：

  ```bash
  python3 benchmarks/terminal-bench-2.0/prepare_dataset.py \
    --source benchmarks/terminal-bench-2.0/dataset \
    --output /data1/users/wangY/benchmarks/tb2-split-v1
  # → 30 train / 19 dev / 40 test
  export HARBOR_DATASET_PATH=/data1/users/wangY/benchmarks/tb2-split-v1/train
  export HARBOR_TASK_COUNT=30
  ```

- Docker socket 权限曾阻塞（用户不在 docker 组），2026-10-08 管理员 `usermod -aG docker` 解决；
  组缓存未刷新时用 `sg docker -c '...'` 兜底。
- 冒烟：`sanitize-git-repo`（train 集内与上游 `extract-elf` 同档题；上游冒烟题属 test 集，已按适配清单改为按划分解析）
  通过，score 1.0、约 5 分 20 秒、$0.0678。
- 单元测试：`uv run python -m unittest discover -s tests -t .` → 17 passed。

## 2. 运行命令

```bash
scripts/run_eval.sh agents.baseline_kira:AgentHarness full 2 50   # 实际并发被收紧为 8，见 §4
```

## 3. 中断与恢复（2026-10-09）

- 首轮 job `h0-terminal-bench-2.0-20261009-1`（04:54–05:36，60 trials = 30 题 × 2）：05:29 起 DeepSeek
  账户余额耗尽，41 个 trial 报 HTTP 402（litellm 包装为 `BadRequestError`）、1 个余额联动限流、1 个未判分超时；
  中断时无一题两次尝试都完成判分，pass@2 口径不成立，当场判定不可作基线。
- 恢复方式：`harbor job resume -p <job目录> -f <错误类型>`——删除指定异常类型的 trial 后只重跑缺失部分，
  结果全部落回**同一 job 目录**，不跨目录拼接。分 3 段执行（脚本与日志在本地 `../runs/`）：
  - 第 1 段 09:21–10:03：重跑 45，判分 15→28，余额再次耗尽；
  - 第 2 段 12:45–14:10：重跑 32（本段消耗 ¥19.55），落定后 56 个 trial 有终判；
  - 第 3 段 14:24–14:55：只重排 4 个未判分 trial（本段消耗 ¥1.96）。
- 第 3 段结论：`query-optimize` 两次再判 `VerifierTimeoutError`（agent 仅 6m07s，判分器把 900s 用满；
  含负载期共 5 次观测全超时）→ 判定为该题在 cpus=1 / 2G 容器内的**真实判分上限**，按未判分记录（score=null）；
  `torch-pipeline-parallelism` 两次均为 agent 用满 900s 的 AgentTimeout，计入 failed；
  此前出现过的 `AttributeError`（上游 `baseline_kira.py` `_parse_tool_calls` 对非 dict 元素的既有缺陷）未复现，
  按协议不修改 H0。
- 教训（供四人协议参考）：① DeepSeek API 并发上限与余额挂钩，队内配置并发 50 必须以充足余额为前提；
  ② harbor 批量 trial 异常时仍以退出码 0 结束，判定必须看 `result.json` 的 `n_errored_trials`；
  ③ 402 会进入 tenacity 重试白耗墙钟——已在本地 `runs/run_h0.sh` 增加余额 preflight 与运行后错误计数摘要。

## 4. 与配置的偏差

- 实际并发 8 < 配置 50（余额收紧所致）。只影响墙钟时间，不影响单题判分与成本，不纳入 config_hash。
- 计费口径：litellm `deepseek/deepseek-flash` 价目（输入 $0.30/M、缓存命中 $0.006/M、输出 $1.20/M）；
  实测输入 ~99% 缓存命中，成本大头是输出 token（含 reasoning，模型默认 effort=high）。
  正常判分 trial 平均 $0.133；对照上游 Opus 4.6 约 $2.8/trial，便宜约 20 倍。
- 账户现状：两次耗尽期不可回收损耗合计 ≈ ¥11；余额剩 ¥28.24。

## 5. 结果与聚合

- 最终 60 trial 目录：40×1.0、17×0.0、3 个未判分（query-optimize ×2 等，聚合到题级为 1 题 score=null）。
- **30 题 pass@2 = 0.70（21 成功 / 8 失败 / 1 未判分，未判分计入分母）**；avg_score 0.7241（21/29）；
  执行成本 $9.7676；tokens 323.3M in / 5.57M out；总墙钟 31084.5 s（含中断与续跑）。
- 题级口径：score=两次 attempt 最高分；tokens/cost/steps/tool_calls 两次合计；wall_time 取两次最大值
  （两次 attempt 并发执行，求和会重复计时）；trace 指向计分 attempt。
- 入库摘要：`results/summary.json`（生成脚本产物，原样提交）+ `results/summary.md`（字段表 + 逐题表 + 口径）。
  逐题完整字段见同目录 `per-task.jsonl`（受 `reproductions/**/results/**` 忽略规则约束，仅本地保留）。
- 原始 job（84 MB）与轨迹（30 MB）本地保留于 `../runs/jobs/h0-terminal-bench-2.0-20261009-1/`、
  `../traces/h0-terminal-bench-2.0-20261009-1/`，路径已被 `.gitignore` 的 runs/、traces/ 规则覆盖。

## 6. 待办与开放项

- `open_item: baseline-result-ownership`——H0 线是独立跑一次，还是复用 Meta-Harness 循环内的 baseline
  结果，待四人统一（两条线同配置，结果应一致）。
- 阶段分离协议（train 搜索 / dev 选择 / test 封存）上游未实现，当前固定 `HARBOR_DATASET_PATH=train`
  保证 test 不触碰；待四人确认后统一实现。
