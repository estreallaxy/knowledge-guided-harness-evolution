# Meta Harness 与 Terminal Bench 2.0 复现交付

本目录包含固定 DeepSeek 条件下的 H0 对照、单轮候选生成、训练评估及启动代码。执行和优化均使用 `deepseek-v4-flash-0731`，百炼为模型接入方式；初始 harness（H0）从 Meta-Harness 官方 KIRA 派生，源码与接线差异可核对。

| 对象 | 通过 | 零分 | 未评分 | 任务数 | 全部尝试 | 摘要 |
| --- | --- | --- | --- | --- | --- | --- |
| 未优化初始 harness（H0） | 13 | 9 | 8 | 30 | 36 | [H0 对照](results/h0/summary.json) |
| 工具参数容错与思考续接（候选 003） | 17 | 10 | 3 | 30 | 38 | [候选结果](results/summary.json) |

两组均为固定 30 题 train 的已有记录。未评分保留在分母，基础设施补跑单独审阅，全部计入消耗；不是 pass@2。训练结果不证明统计显著改进或泛化。账单未知，未显式设置 seed。

## 安装与环境

从仓库根目录执行：

```bash
cd reproductions/liYK/meta-harness/terminal-bench-2.0
python3.12 -m venv .venv
.venv/bin/python -m pip install -r code-adaptation/requirements-lock.txt
.venv/bin/python code-adaptation/launch.py prepare
```

需要可访问的 Docker 和 linux/amd64 镜像支持。按主机环境配置 Docker，远程 Docker 可通过 `DOCKER_HOST` 指定。已有实验环境为 4 CPU、8 GiB 的 Lima/Docker，linux/amd64。共享 benchmark 只读，数据副本写入本目录 `data/tb2-split-v1/`。

```bash
export DOCKER_DEFAULT_PLATFORM=linux/amd64
export PYTHONDONTWRITEBYTECODE=1
.venv/bin/python code-adaptation/launch.py check
```

`check` 验证固定数据、agent 导入和 Docker 连通性，不启动任务。固定划分 train/dev/test = 30/19/40；评估只接受 train，优化器只读取允许的训练证据。

## 评估与优化入口

默认仅预览，不调用模型：

```bash
.venv/bin/python code-adaptation/launch.py evaluate
.venv/bin/python code-adaptation/launch.py evaluate --train
.venv/bin/python code-adaptation/launch.py evaluate --agent agents.deepseek_candidate_003:AgentHarness --train
```

默认 smoke 为 train 中的 `regex-log`，`--train` 覆盖全部 30 题，`--tasks` 可选 train 子集。并发 1、每题 1 次、任务原生时限；优化会话最多 2400 秒，不人为限制输出/思考 token。真实启动需加 `--execute`，并提供环境变量 `BAILIAN_API_KEY`、`BAILIAN_OPENAI_COMPATIBLE`，凭据不存入仓库。

```bash
.venv/bin/python code-adaptation/launch.py evaluate --train --execute
```

也可用 `with_service.py --service <服务名> -- <命令>` 从本机服务配置加载变量。服务或预算变化单独记录，保持对照可比。

训练证据保存在本目录 `runs/`；原始产物留在运行机器，Git 保存摘要和轻量索引。迁移、导出和优化接口为：

```bash
.venv/bin/python code-adaptation/import_history.py --help
.venv/bin/python code-adaptation/export_train.py --help
.venv/bin/python code-adaptation/propose.py --evidence runs/<训练证据目录> --name deepseek_candidate_<标识>
```

优化器默认预览；加 `--execute` 后读取白名单源码和冻结 train 证据、写新候选，评估单独运行，禁止覆盖既有候选。不提供隐藏评分脚本、verifier 日志或 dev/test 证据；失败与重试累计消耗保留。

## 验证与证据范围

从本目录运行：

```bash
PYTHONPATH=code-adaptation:../code/reference_examples/terminal_bench_2 .venv/bin/python -m unittest discover -s code-adaptation/tests -v
.venv/bin/python code-adaptation/verify_delivery.py
.venv/bin/python ../../../../knowledge/source-packets/verify_liyk.py
```

18 项合成检查覆盖候选行为、模型接线、训练边界和优化工具往返；来源检查核对六包固定材料及主张映射。检查不产生 benchmark 分数。当前入口未新增真实任务试次，已有结果对应冻结的实际执行源码。

独立实现对应见 [复现报告](notes/reproduction-report.md)，原始运行索引见 [证据索引](notes/evidence-index.json)，源码来源见 [接线说明](code-adaptation/README.md)。官方参考源码、共享 benchmark 和评分器未修改。共同条件验收待团队审阅；dev 未完成成对评估，test 和第二轮优化未开展。
