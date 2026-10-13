# H0 × Terminal-Bench 2.0 复现记录（赵星源）

记录时间：2026-10-13。本文件只覆盖 **H0 基线运行**；运行入口的代码适配清单与验证
（依赖源、模型接线、数据集开关、沙箱白名单、冒烟题解析）在
`../../meta-harness/terminal-bench-2.0/notes/README.md`，两条线共用同一入口与同一套执行条件。
凭据不入库，只登记变量名。

## 1. 环境与准备

- 运行入口：`../../meta-harness/code/reference_examples/terminal_bench_2/`（`uv sync` 已就绪，
  harbor 0.18.0 / terminal-bench 0.2.18 / litellm 1.84.10）；`agents/baseline_kira.py`
  与本单元 `code/terminus-kira/baseline_kira.py` 是同一文件（sha256 `e06b9273…`）。
- 沙箱：本地 Docker（`HARBOR_ENVIRONMENT=docker`），89 个任务镜像本机全量缓存，无需云密钥。
- 数据：`export HARBOR_DATASET_PATH=/data1/users/zhaoXY/benchmarks/tb2-split-v1/train`（30 题，
  由仓库冻结清单 `benchmarks/terminal-bench-2.0/split-v1.json` 生成）。
- 凭据：`<运行入口>/.env` 只放 `DEEPSEEK_API_KEY`（600 权限，已被 .gitignore 挡住）。
- **模型与实际版本**（按 `docs/research-plan.md` §2.2「统一模型配置」的要求记录）：运行使用
  `deepseek/deepseek-v4-flash`（litellm 形式）。2026-10-13 直接核实 API：`/models` 仅提供
  `deepseek-flash` 与 `deepseek-v4-pro`；用未知模型名调用会被明确拒绝（错误信息列出支持列表）；
  `deepseek-v4-flash` 是**被接受的别名**，其响应中的 `model` 字段为 `deepseek-flash`。
  即本轮实际服务模型 = **`deepseek-flash`（DeepSeek V4.1 Flash）**，调用日期 2026-10-13。
  后续轮次可直接改用规范 id `deepseek/deepseek-flash`（同一模型）。

**预检（全部通过后才发车）**

| 预检 | 结果 |
| --- | --- |
| 离线单测（代码路径回归） | 52 项 OK |
| 余额 preflight（脚本内） | ¥99.46 ≥ 阈值 ¥80 |
| 划分/冒烟题解析 | train 30 题；冒烟题解析为 `fix-code-vulnerability`（非 test 集任务） |
| oracle 端到端（不调 LLM） | 1/1，reward 1.0，18 秒 —— docker、题镜像、verifier 链路全通 |

## 2. 运行命令

```bash
# 条件见 ../configs/h0.yaml；实跑并发 10（见 §5 偏差）
cd ../../meta-harness/code/reference_examples/terminal_bench_2
export HARBOR_MODEL="deepseek/deepseek-v4-flash"
export HARBOR_ENVIRONMENT=docker
export HARBOR_DATASET_PATH=/data1/users/zhaoXY/benchmarks/tb2-split-v1/train
bash scripts/run_eval.sh agents.baseline_kira:AgentHarness full 2 10 \
  --job-name h0-terminal-bench-2.0-20261013-1 \
  --jobs-dir <本单元>/runs/jobs -y
```

运行脚本（含余额/划分预检与运行后错误结算）：`../runs/run_h0.sh`（本地不入库）。

**补跑（本次实际执行过一次，2026-10-13）**

```bash
cd ../../meta-harness/code/reference_examples/terminal_bench_2
export PYTHONPATH="$PWD"              # 必须：harbor 需要 import agents.baseline_kira
set -a; source .env; set +a           # 只需要 DEEPSEEK_API_KEY
export HARBOR_MODEL="deepseek/deepseek-v4-flash" HARBOR_ENVIRONMENT=docker
uv run harbor job resume -p <job 目录> -f BlockError -y
```

- `-f BlockError` 会先删掉该类错误的 trial，再只补跑缺失部分，结果落回**同一 job 目录**；
  agent/模型/数据集/次数都取自 job 内 `config.json`，不需要重传参数。
- 两个坑：① 漏 `PYTHONPATH` 会以 `Failed to import module 'agents.baseline_kira'` 立刻失败；
  ② `harbor run` 在作业启动时就会写一份 `result.json` 占位（`finished_at: null`），
  判断"跑完没有"要看 `finished_at` + `n_pending_trials`/`n_running_trials`，不能只看文件存在。

## 3. 结果

| 项 | 值 |
| --- | --- |
| run id | `h0-terminal-bench-2.0-20261013-1`（首轮 2026-10-13T00:56:12 → 02:56:34；resume 补跑至 06:49） |
| **pass@2（任务级，主口径）** | **19/30 = 0.6333**；avg_score（计入判分题）= 0.6552 |
| **trial-level micro pass rate** | 33/60 = 0.5500（与 main 上各线文档同一术语） |
| 成功 / 失败 / 未判分（题级） | 19 / 10 / 1 |
| trials | 60 全部完成（出错 19、重试 0、取消 0；异常分布：`AgentTimeoutError` 16、`VerifierTimeoutError` 3） |
| 成本 / tokens / 墙钟 | $9.5112 · 338.8M in / 5.26M out · 首轮 120 分钟 + resume 25 分钟（并发 10） |
| 未判分一题 | `query-optimize`：两次 `VerifierTimeoutError`（判分器 900s 用满，与 10-08 轮一致，属该题在容器内的真实判分上限） |
| resume 记录 | `caffe-cifar-10` 首轮两次 `BlockError`（"Infrastructure API blocked for 600s"，出在 harbor 的 tmux 会话读取层），用 `harbor job resume -p <job> -f BlockError` 删掉该类 trial 后补跑；补跑两次均为 `AgentTimeoutError`（1200s 用满）、reward 0.0，**本题由"未判分"变为"确定失败"**，结果落回同一 job 目录 |
| 入库摘要 | `../results/summary.md` + `../results/summary.json`（由 `../summarize.py` 从本地 job 目录生成） |
| 原始产物（不入库） | `../runs/jobs/h0-terminal-bench-2.0-20261013-1/`（含每 trial 的 `agent/trajectory.json`、`verifier/`） |

## 4. 与另外两轮同配置 H0 的对照（重要）

同一 H0、同一模型、同一 30 题 train，目前已跑过三轮：

| 轮次 | 任务级 pass@2 | trial-level micro | 成本 | 并发 |
| --- | --- | --- | --- | --- |
| 本轮（zhaoXY H0 线，10-13，含 resume） | **0.6333**（19/30） | 0.5500（33/60） | $9.51 | 10 |
| zhaoXY meta-harness 线（10-08） | 0.7333（22/30） | 0.6667（40/60） | $10.13 | 10 |
| wangY H0 线（10-09） | 0.70（21/30） | — | $9.77 | 8 |

逐题对照（本轮 vs 10-08）：**19 题两轮都成功**；**0 题翻转向上**；**3 题翻转向下**——
`compile-compcert`（2400s 时限）、`dna-assembly`（1800s）、`make-mips-interpreter`（1800s），
三题本轮均为**两次都跑满时限的 AgentTimeoutError**。另一处差异是 `caffe-cifar-10`：
10-08 拿到 0.0 终判，本轮首轮为 BlockError、补跑后同样判 0.0（两次 1200s 超时）。

**判读**：三轮的分差（0.63 / 0.70 / 0.73）主要来自**超时类失败**，不是配置差异——
本轮 14 个 AgentTimeout trial（上一轮 10 个），且本轮宿主负载更低（启动时 load 4.4），
说明超时不是"高负载假失败"，而是这些长任务本身就在时限边缘。**这组数据给出本环境的
噪声底线：同配置重跑，任务级 pass@2 在 0.63~0.73 间浮动（±3 题）。后续比较 Method
增益时必须超过这个幅度，或提高重复次数。**

## 5. 与配置的偏差

- **并发 10 < 配置默认 50**：余额收紧时 DeepSeek 并发上限随之下降（队友侧实测 8 可用）。
  并发只影响墙钟，不影响单题判分与成本，不纳入 config_hash。
- **未判分题计入分母**（口径见 `../results/summary.md`）：唯一未判分题 `query-optimize`
  按该题真实判分上限记录；`caffe-cifar-10` 的基础设施 BlockError 已用 resume 补跑成
  确定判分（0.0），不再占用"未判分"名额。
- **resume 的计时**：job 记录的 21195 s 是首启→最终结束的跨度（含 03:00~06:24 的中断间隔）。
  实际计算墙钟 = 首轮 120 分钟 + 补跑 25 分钟；比较运行时长时不要用 job 跨度。
- 计费口径：litellm `deepseek/deepseek-flash` 价目；本轮无缓存命中（`n_cache_tokens=0`），
  与 10-08 轮相同。

## 6. 待办与开放项

- **`baseline-result-ownership`**：H0 线独立跑一次，还是复用 Meta-Harness 循环内的 baseline
  结果（两条线同配置，结果应一致但不同轮）。
- **VerifierTimeoutError 是否计为失败**：本单元按 trial 原样记录、题级按未判分计入分母；
  跨线比较前须统一口径。
- **并发口径**：配置默认 50 vs 实测 10（余额充足时可再测）。
