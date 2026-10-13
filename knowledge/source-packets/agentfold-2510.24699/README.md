# AgentFold: Long-Horizon Web Agents with Proactive Context Management

| 内容 | 位置 |
| --- | --- |
| 来源元数据 | [source-packet.json](source-packet.json) |
| 论文 v1 | [paper/paper-v1.pdf](paper/paper-v1.pdf) · [文本](paper/paper-v1.txt) |
| 官方核心代码 | [`official-code/`](official-code/)（`AgentFold/infer.py` + 根 `inference/` 工具） |
| 论文与代码定位 | [exact-source-anchors.md](exact-source-anchors.md) |
| 配置和运行入口 | [configs-and-examples.md](configs-and-examples.md) |
| 测试与论文结果 | [tests-and-reported-results.md](tests-and-reported-results.md) |

## 这篇论文解决什么

长程 web agent 的上下文管理存在取舍：ReAct 式 agent 累积原始历史导致上下文饱和；
每步固定摘要全部历史又会不可逆地丢掉关键细节。AgentFold 让模型在每一步**同时输出一个
「折叠指令」和一个工具调用**，指令可以在两个尺度上工作（细粒度合并 vs 把整段子调查压成结论），
并用「多尺度状态摘要 + 最近一次交互保真」的结构替换原始历史，再用 SFT 训练出来。

与我们 harness 的关系：这是「上下文压缩」方向的另一极——ACON 压缩已有上下文，
AgentFold 让 agent 主动管理并折叠状态，两者可以组合也可以互相替代。

## 快照状态

`official-code/` 已入库，固定 revision `f72f75d8c3eb842f2bbbab096a12206ff66e270f`
（2026-10-13 取得）。**明确缺失**：

- 训练数据、SFT 训练脚本与 `AgentFold-30B-A3B` 权重**不在仓库内**，仓库只给推理侧代码。
- `serve.sh` 里 `MODEL_PATH` 留空，需要自备权重并用 vLLM 起服务；`infer.py` 默认连本机
  `localhost:8000-8005`，并额外用 `gpt-oss-120b` 起一个 8006 端口。
- 上游未提供单元测试目录，测试入口记为未知。
- 快照布局：上游 `WebAgent/AgentFold/` 拍平为顶层 `AgentFold/`；仓库级 `FAQ.md`、`.env.example`
  （仅占位符）、`.gitignore` 与 `Tech_Report.pdf` 已纳入。上游 `README.md` 中指向 `./WebAgent/`、
  `./evaluation/` 及 `assets/` 图片的引用因快照布局差异改为纯文本。

## 与本地实验的关系

本包只保存论文与官方代码，不含本地运行结果。方法实现（Method）尚未分配，本阶段不做本地 demo。
论文结果是 **30B 级模型训练后**的表现，不能直接等同于固定 `deepseek-v4-flash` 的 harness 收益。
