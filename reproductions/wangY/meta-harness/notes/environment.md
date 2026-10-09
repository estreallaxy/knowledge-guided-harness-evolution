# 环境适配记录（王懿）

记录时间：2026-10-07 ~ 2026-10-09
适用范围：`code/reference_examples/terminal_bench_2/`（Meta-Harness + Terminal-Bench 2.0 复现）

本文件说明**相对上游代码做了哪些改动、为什么改、怎么验证的**。凭据一律不写入仓库，只登记变量名。

---

## 1. 模型与端点

| 项 | 上游默认 | 本机实际 |
| --- | --- | --- |
| 执行模型 | `anthropic/claude-opus-4-6` | `deepseek/deepseek-flash` |
| 优化模型（提议 Agent） | Claude Code CLI + `--model opus` | Claude Code CLI 经 DeepSeek 的 Anthropic 兼容端点 |
| 端点 | Anthropic 官方 | `https://api.deepseek.com/v1`（OpenAI 兼容，litellm 用）/ `https://api.deepseek.com/anthropic`（claude CLI 用） |

团队约定的模型名 `deepseek-v4-flash` 在本机端点上对应的模型 id 是 `deepseek-flash`
（DeepSeek-V4.1-Flash：上下文 1,048,576 / 最大输出 393,216 / 支持图像输入与 function calling）。

补充实测（2026-10-09）：`GET /v1/models` 只列出两档——`deepseek-flash`（V4.1-Flash）
与 `deepseek-v4-pro`（V4-Pro）；`deepseek-v4-flash` 作为别名可直接调用，返回体的 `model`
字段同为 `deepseek-flash`。即团队内写 `deepseek-v4-flash` 或 `deepseek-flash` 是同一模型，两条实验线可比。
另：该模型默认 reasoning effort 为 `high`（`/v1/models` 的 `effort.default_level`），实测响应含
`reasoning_content`。

**litellm provider 前缀的实测差异（这决定了用哪个前缀）：**

- `deepseek/deepseek-flash`：原生接受 `reasoning_effort`，支持 tool calling。
- `openai/deepseek-flash`：报 `UnsupportedParamsError: openai does not support parameters: ['reasoning_effort']`。

代码中 `baseline_kira.py` 已带 `drop_params=True` 兜底，但仍统一使用 `deepseek/` 前缀。
`litellm` 的 deepseek provider 读取 `DEEPSEEK_API_KEY`。

**优化 Agent 路径的关键结论（实测）：** `claude_wrapper.build_command()` 会传
`--setting-sources ""`，这**禁用 settings.json**，provider 配置必须来自进程环境变量。
实测：继承 `ANTHROPIC_BASE_URL` / `ANTHROPIC_AUTH_TOKEN` 时 `claude -p` 正常返回；
清空这两个变量后返回 `Not logged in · Please run /login`。
因此 `meta_harness.py` 的 `run_cmd` / `harbor_run` 与 `claude_wrapper` 的子进程都要显式传播这两个变量。

## 2. 环境变量契约

`scripts/run_eval.sh` 会 `source <terminal_bench_2>/.env`（已被 `.gitignore` 忽略）；
`meta_harness.py` 顶部有 `load_dotenv(override=True)`。
变量名清单见 `code/reference_examples/terminal_bench_2/.env.example`。

| 变量 | 必需 | 说明 |
| --- | --- | --- |
| `DEEPSEEK_API_KEY` | 是 | litellm 的 deepseek provider 密钥 |
| `ANTHROPIC_BASE_URL` | 是 | claude CLI 端点，`https://api.deepseek.com/anthropic` |
| `ANTHROPIC_AUTH_TOKEN` | 是 | claude CLI 凭据 |
| `HARBOR_API_BASE` | 否 | 覆盖默认 `https://api.deepseek.com/v1` |
| `HARBOR_MODEL` | 否 | 覆盖默认 `deepseek/deepseek-flash` |
| `HARBOR_DATASET_PATH` | 否 | 设置后用 Harbor `-p` 读本地划分目录；不设则跑 registry 全量 89 题 |
| `HARBOR_ENVIRONMENT` | 否 | 默认 `docker`；可选 `runloop` / `modal` |

`.env` 只放凭据与端点，不要放 `HARBOR_MODEL` / `HARBOR_ENVIRONMENT` 等运行参数——
`run_eval.sh` 的 `source` 会覆盖外部环境，而 `tests/test_meta_harness.py` 依赖这些变量的默认值。

## 3. 代码改动清单

| 文件 | 改动 | 原因 |
| --- | --- | --- |
| `pyproject.toml` | 移除 `[tool.uv.sources]` 中指向 git commit 的覆盖，改为从 PyPI 装 `terminal-bench==0.2.18` | 上游 pin 的 commit `1a6ffa9674b571da0ed040c470cb40c4d85f9b9b` 已从远端消失，`uv sync` 报 `not our ref`；版本号 pin 未变 |
| `meta_harness.py` | `MODEL` / `API_BASE` / `MODEL_INFO` 改为环境变量驱动，新增 `DATASET_PATH`、`EVAL_TASK_SET`、`N_EVAL_TASKS` | 上游硬编码 Anthropic 模型与全量数据集 |
| `meta_harness.py` | `run_cmd` / `harbor_run` 传播 `DEEPSEEK_API_KEY`、`ANTHROPIC_AUTH_TOKEN`、`ANTHROPIC_BASE_URL`、`HARBOR_*` | 见第 1 节「优化 Agent 路径的关键结论」 |
| `meta_harness.py` | `propose_claude` 增加 provider 环境变量 preflight，缺失时提前返回 | 否则要等到子进程失败才发现，浪费一轮迭代 |
| `meta_harness.py` | `render_task_prompt` 的硬编码 `(Opus)` 与数据集描述改为按实际配置生成（新增 `_dataset_line()`） | 避免优化 Agent 读到错误的模型与规模 |
| `meta_harness.py` | 冒烟题由固定 `extract-elf` 改为按数据集解析（`_resolve_smoke_task()`，可用 `HARBOR_SMOKE_TASK` 覆盖） | 见第 5 节：`extract-elf` 属于 test 集，在 train 目录下不存在且会造成测试集泄漏 |
| `scripts/run_eval.sh` | 默认 `MODEL` → `deepseek/deepseek-flash`，默认 `HARBOR_ENVIRONMENT` → `docker`，`case` 接受 `docker` | 本机无云沙箱密钥，用 Harbor 内置的本地 Docker |
| `scripts/run_eval.sh` | 透传 `--ak api_base=... --ak model_info={...}`（仅当 `HARBOR_API_BASE` 非空）；新增 `HARBOR_DATASET_PATH` 支持（`-p`） | litellm 未登记 `deepseek-flash`，需显式上下文档位；划分数据集需从本地目录读取 |
| `scripts/run_eval.sh` | 恢复可执行位（`100644` → `100755`） | 仓库 vendoring 时丢了 exec 位，`tests/test_meta_harness.py` 直接执行该脚本会 `PermissionError` |
| `tests/test_meta_harness.py` | 默认环境断言 `runloop` → `docker`，新增模型/端点/数据集透传断言，测试环境变量清理补全 | 使测试反映本机适配后的行为 |
| `.env.example`（新增） | 登记 DeepSeek 相关变量名 | 上游无此文件 |

**不需要改动的部分（已核实）：**

- `anthropic_caching.py`：`add_anthropic_caching()` 对非 anthropic/claude 模型名直接 no-op。
- `agents/baseline_kira.py`：`_call_llm_with_tools` 已支持 `api_base` 与 `drop_params=True`；
  缓存在 deepseek 下自动跳过。
- `Terminus2._resolve_model_info` / `get_model_output_limit`：对未登记模型安全回退到显式传入的 `model_info`。

## 4. 本地验证记录

| 检查 | 命令 | 结果 |
| --- | --- | --- |
| 依赖安装 | `uv sync` | 退出码 0；`harbor 0.18.0` / `litellm 1.84.10` / `python-dotenv 1.2.2` / `tenacity 9.1.4` / `terminal-bench 0.2.18` |
| 单元测试 | `uv run python -m unittest discover -s tests -t .` | 17 passed |
| Agent 导入路径 | `uv run python meta_harness.py --validate-agent agents.baseline_kira:AgentHarness` | `OK` |
| tool calling | `litellm` + `deepseek/deepseek-flash` + 显式 `api_base` | `finish_reason: tool_calls`，正常 |
| claude CLI 路径 | `claude -p ... --model opus --setting-sources ""` | 继承 provider 环境变量时返回预期结果 |

**Docker 权限（已解决，2026-10-08）：** 曾因 `permission denied /var/run/docker.sock`
（socket 属 `root:docker 660`、用户不在 docker 组）阻塞；管理员执行 `usermod -aG docker` 后解决，
会话内组缓存未刷新时用 `sg docker -c '...'` 兜底。冒烟测试（sanitize-git-repo）已通过：
score 1.0、约 5 分 20 秒、$0.0678，产物在 `jobs/smoke-kira-baseline/`。
H0 首轮正式运行见第 6 节。

## 5. 数据集划分

仓库固定划分为 30 train / 19 dev / 40 test，清单见
`benchmarks/terminal-bench-2.0/split-v1.json`，说明见 `benchmarks/terminal-bench-2.0/README.md`。

本机已按仓库说明生成独立划分目录（在仓库外，不指向任何其他成员的工作区）：

```bash
python3 benchmarks/terminal-bench-2.0/prepare_dataset.py \
  --source benchmarks/terminal-bench-2.0/dataset \
  --output /data1/users/wangY/benchmarks/tb2-split-v1
# → Prepared and verified ...: 30 train / 19 dev / 40 test
```

运行方式：

```bash
export HARBOR_DATASET_PATH=/data1/users/wangY/benchmarks/tb2-split-v1/train
```

**冒烟题与测试集泄漏（已修）：** 上游 `SMOKE_TEST_TASK = "extract-elf"` 硬编码，
而 `extract-elf` 在固定划分里属于 **test** 集。两处问题：

1. 冒烟测试通过 `run_eval.sh` 调用 Harbor，而该脚本此时已带 `-p <train>`，
   train 目录下没有这道题 → 冒烟必然失败；
2. 即便目录里存在，冒烟产生的轨迹也会被优化 Agent 读到，违反「封存测试集不参与优化」。

改为 `_resolve_smoke_task()`：未配置本地划分时保持上游行为；配置了则优先取 train 集的
`sanitize-git-repo`（medium / 专家 30min，与 `extract-elf` 同档），否则取该目录下实际存在的题。
`HARBOR_SMOKE_TASK` 可显式覆盖。四种情形已实测：registry → `extract-elf`、
train → `sanitize-git-repo`、dev → `build-pov-ray`、test → `adaptive-rejection-sampler`。

**待与其他三人对齐的协议问题（尚未实现）：** 上游 `meta_harness.py` 用同一套任务做搜索与选择；
研究计划要求「优化器只看 train、dev 仅供选择候选、test 到最终评估才运行」。
当前代码只做到「可以指向任一划分目录」，搜索/选择/最终评估的阶段分离需要在四人确定协议后统一实现。
在此之前，复现运行固定 `HARBOR_DATASET_PATH=.../train`，保证 test 不被触碰。

## 6. H0 首轮运行中断：DeepSeek 账户余额耗尽（2026-10-09）

**运行方式**：`setsid nohup sg docker -c 'bash runs/run_h0.sh'`（脱离会话启动，实测终端关闭不影响后续执行）；
job `h0-terminal-bench-2.0-20261009-1`，04:54 启动、05:36 结束，并发 8。

**结果**（60 trials = 30 题 × 2 次）：

| 结局 | 数量 | 说明 |
| --- | --- | --- |
| 正常判分 | 17 | 15 × 1.0；2 × 0.0（extract-moves-from-video、gcode-to-text，AgentTimeout 后仍执行判分） |
| `Insufficient Balance` | 41 | HTTP 402，litellm 包装为 `BadRequestError`；约 05:29 起集中出现 |
| 余额联动限流 | 1 | `RateLimitError`：`concurrency is 5 ... based on your remaining balance` |
| AgentTimeout 未判分 | 1 | caffe-cifar-10，在 job 收尾时刻被终止，verifier 未执行 |

- **中断时没有任何一道题两次尝试都完成判分**（pass@2 口径不成立）→ 当场判定不可作基线；
  后经 harbor job resume 分段补跑，**同一 job 目录**补齐为完整基线（见下文第 2/3 段），未跨目录拼接。
  原始证据在 `runs/jobs/h0-terminal-bench-2.0-20261009-1/`（60 个 trial 目录，各含 `exception.txt` / `result.json`）。
- **教训 1**：DeepSeek 的 API 并发上限与账户余额挂钩——余额下降并发上限收紧（本轮临界时被限到 5），
  余额为零后全部请求 402。队内配置默认并发 50（`configs/h0.yaml`），必须以充足余额为前提。
- **教训 2**：harbor 在批量 trial 异常时仍以退出码 0 结束（日志里 `H0-EXIT rc=0`）。
  判定成功与否必须看 `result.json` 的 `n_errored_trials` / `n_cancelled_trials`，不能只看退出码。
- **教训 3**：402 被 litellm 包成 `BadRequestError` 后仍进入 tenacity 重试，
  直到重试耗尽或任务超时，白耗墙钟与沙箱时间。已在 `runs/run_h0.sh` 增加
  **余额 preflight**（余额不可用直接 abort、低于 20 元告警）与**运行后错误计数摘要**。
- **账户现状**：`GET https://api.deepseek.com/user/balance` → `is_available: false`、余额 `-0.13 CNY`（已透支）。
  查询命令：`curl -s https://api.deepseek.com/user/balance -H "Authorization: Bearer $DEEPSEEK_API_KEY"`
- **成本**：本轮估算 $3.20；完整重跑一轮粗估 $5–10（账户按人民币结算）。
- **复现动作（2026-10-09 09:21 执行）**：改用中断恢复而非全量重跑——harbor 自带
  `harbor job resume -p <job目录> -f <错误类型>`：删除指定错误类型的 trial 后**只重跑缺失部分**，
  已完成的保留，最终汇总回**同一 job 目录**（不跨目录拼接，符合 results 协议）。
  本次删除 45 个（41 BadRequest + 1 RateLimit + 3 AgentTimeout），保留 15 个无异常结果，
  重跑 45 个；脚本 `runs/run_resume.sh`。以后再遇中断可重复续跑，进度不废。
  续跑第 1 段（09:21–10:03）完成 13/45，有效判分 15→28（22×1.0、6×0.0）；余额再次耗尽（-0.24）。
  **第 2 段策略（待充值后执行）**：余 32 个未判分 = 30 BadRequest + 1 VerifierTimeout + 1 caffe AgentTimeout。
  对 AgentTimeout 按成因甄别：gcode-to-text / raman-fitting 两轮都停在 ~15m39s（≈900s 任务时限）、
  extract-moves-from-video ~31m06s（≈1800s 时限）→ 属任务自身时限，保留 0 分终判、不再重跑；
  caffe-cifar-10 的超时结束于 10:03:31 ≈ job 被余额中断时刻（已运行 41m50s，未触已知时限）→ 属环境性中止，
  由 `runs/run_resume.sh` 显式单独重排。第 2 段 = 类型过滤删 31（30 BR + 1 VT）+ 手动重排 1 = 重跑 32、保留 28。

**第 2 段结果（12:45–14:10，rc=0）**：32 个重跑全部落回同一 job 目录，本段消耗 ¥19.55（49.75 → 30.20）。
段末盘点 60 个目录：**40 × 1.0、16 × 0.0**（7 个无异常判 0 + 9 个 AgentTimeout 后仍判 0）、**4 个未判分**：

| 未判分 trial | 异常 | 情况 |
| --- | --- | --- |
| query-optimize ×2（JTbRGaE / khgGUhr） | `VerifierTimeoutError` | 判分器 900s 超时；含 seg1 的 u6GTjbY 共 3 次观测，均发生在 8 并发负载下。该题 test.sh 需在 cpus=1 / 2G 容器内 apt-get + 装 uv 后 pytest |
| torch-pipeline-parallelism__NUzzQyG | `AttributeError` | 上游 `agents/baseline_kira.py:423`（`_parse_tool_calls`，经 835 行调用）假设 commands 列表元素为 dict，模型偶发返回字符串 → `cmd.get` 崩溃。上游 H0 既有缺陷，按协议不改 H0 |
| torch-pipeline-parallelism__T4Rtnfd | `AgentTimeoutError`（无 reward） | AT 记录（14:10:12）与 job 进程退出（14:10:13）竞态，verifier 未执行；非任务时限判定 |

**第 3 段（最后一段，14:24 启动）**：只重排上述 4 个未判分 trial：

- query-optimize ×2、NUzzQyG 走 `-f VerifierTimeoutError` / `-f AttributeError` 类型过滤
  （harbor 按 `exception_type` 字符串精确匹配，实现见 venv 内 `harbor/cli/jobs.py`）；
- T4Rtnfd 手动重排；**不放宽 AgentTimeoutError 通用过滤**——其余 9 个 AT 都带有效 0.0 终判
  （重跑复现过的真实时限），加入过滤会白跑 9 题。

本段在本 job 无并发负载的条件下运行（其余 56 个 trial 已完成；宿主机为多人共用、其他成员容器不受控也不干预）。
若 query-optimize 判分器在空闲下仍超时 → 判定为该题在 cpus=1 容器内的真实判分上限，
按「未判分」记录（`score=null` + 异常说明），并在 summary 中注明。

**第 3 段结果（14:24–14:55，rc=0）**：4 个重排全部落定——query-optimize 2/2 再判 `VerifierTimeoutError`：
agent 阶段仅 6m07s，判分器把 900s 用满（apt + uv + CPython 下载完成后，pytest 六个用例跑不完）→
判定为该题在 cpus=1 容器内的**真实判分上限**（含负载期共 5 次观测全超时，与本 job 并发无关）。
torch-pipeline-parallelism 2/2 仍为 AgentTimeout（agent 各用满 900s；gXWdB8B 的 verifier 判出 0.0，
VMRbwbK 的 verifier 同样 900s 超时、无 reward）；上次的 AttributeError 未复现（transient 确认）。
**最终 60 目录：40×1.0、17×0.0、3 个未判分**（query-optimize ×2、VMRbwbK 1 条）。本段消耗 ¥1.96
（30.20 → 28.24）。协议记录已按 §8 产出：30 题 pass@2 = 0.70（21 成功 / 8 失败 / 1 未判分）。

## 7. 成本核算口径与对照（2026-10-09）

- 计费口径（litellm 价格表 `deepseek/deepseek-flash`）：常规输入 $0.30/M，**缓存命中输入 $0.006/M**，
  输出 $1.20/M。实测输入 token 约 99% 命中缓存、按 $0.006/M 计（agent 每步重发前缀、命中率高），
  因此**成本大头是输出 token（含 reasoning）而不是上下文体积**：25 个正常判分 trial 共 $3.33，
  其中输出约 $2.24（67%），单题平均输出 ~74K tokens（reasoning effort 为模型默认 high）。
- 单次成本：正常判分 $0.133/trial（≈¥1.0）；最重的题（dna-assembly、make-mips-interpreter）单次封顶 $0.44。
- （第 1 段末口径）现有 60 个 trial 目录合计 $4.745：已判分的 28 个占 $3.96（84%），余额中断的 32 个占 $0.78（16%，
  多为早期即死）。另首轮被删的 45 个 trial 的部分消耗约 $0.9（由账户余额差额推得，目录已删无法精确归集）。
- 对照上游 README（本仓库 vendored 副本 `README.md`「Runtime And Cost」）：
  89×2、Opus 4.6、并发 50 ≈ **$500/iteration**（折合 ~$2.8/trial）。本机 deepseek-flash 为 $0.08–0.14/trial，
  **便宜约 20 倍**；完整干净跑完 H0（60 trial）预计 ≈ $8（¥55–60）。
- 配置核对：模型、温度 0.7、2 attempts、各任务 task.toml 自带超时（实测 900s / 1200s / 1800s 档）均与协议一致；
  唯一偏差是运行并发 8 < 配置 50（DeepSeek 并发上限随余额收紧所致），只影响墙钟时间、不影响单题成本。
- 结论：花销与配置无异常，事故期（两次余额耗尽）的不可回收损耗合计 ≈ ¥11；用足余额、一次跑完是唯一大杠杆。

## 8. 结果产物与聚合口径（2026-10-09）

- **协议记录**：`experiments/results/terminal-bench-2.0/h0-terminal-bench-2.0-20261009-1/`
  （`per-task.jsonl` 30 行 + `summary.json` + `traces/`：两次 attempt 的 `trajectory.json`）。
  生成脚本 `runs/build_results.py`（幂等，traces/ 每次重建）。根 `.gitignore` 的
  `experiments/results/*` 已忽略原始记录，运行产物不入库、字段文档入库。
- **原始 job 目录**：60 个 trial 的 cast/pane/日志/result 全部保留在
  `runs/jobs/h0-terminal-bench-2.0-20261009-1/`（第 3 段完成后从 vendored 仓库 `jobs/` 迁入，
  对齐 experiments/README「原始运行产物保存在各成员工作区的 runs/」）。
- **逐题聚合口径**（harbor 一个 trial 目录 = 一个任务的一次 attempt；协议要求一行一个任务）：
  score = 两次 attempt 最高分（pass@2）；status = success(任一 1.0) / failed(有 0.0) /
  timeout(全部为超时类异常) / error；tokens_in/out、cost、steps、tool_calls = 两次合计（资源口径）；
  wall_time_s = 两次中最大（任务时间窗；两次尝试并发执行，求和会重复计时）；error = 按 started_at
  排序的各 attempt 异常拼接（无异常为 null）；trace_path 指向计分 attempt 的轨迹。
- **config_hash**：sha256(规范化 JSON)，内容 = benchmark id + commit + split 清单 sha256 +
  三划分规模 + execution 块（模型 / 温度 / api_base / docker / 2 attempts）+ 方法块
  （line=h0、import_path、`baseline_kira.py` 的 sha256）；字面量见 `runs/build_results.py`
  的 EXECUTION/METHOD 常量。并发数 8 为运行强制偏差、不影响评分，不纳入哈希（§7 与 configs/h0.yaml）。
- **缺失记录**：若任务两次都未判分，`score=null`（不删键）、error 记异常文本；此类可解释缺失
  （如判分器超时）的原因说明在 §6 与交付汇报中给出。其余缺失按 `results/README.md` 检查清单逐项核对。
- **本轮最终数字**：30 题 pass@2 = 0.70（21/30），avg_score = 0.7241（21/29，query-optimize 未判分不计），
  执行成本 $9.7676（job `result.json` 口径）；60 个 trial 合计 tokens 323.3M in / 5.57M out
  （输入 ~99% 为缓存命中，成本大头是输出，见 §7）。
