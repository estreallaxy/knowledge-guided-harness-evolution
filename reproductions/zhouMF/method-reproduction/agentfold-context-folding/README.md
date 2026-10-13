# Proactive Context Folding

## 什么时候使用

适用于几十步以上的长程任务，原始历史已出现噪声累积或上下文溢出，而固定全量摘要会丢失关键证据时。

## 机制

每步由 agent 选择细粒度折叠（保留近期细节）或深度整合（抽象完成/失败的多步子任务），把历史维护为多尺度状态摘要加最近高保真交互。

## 本项目边界

该论文以训练后的网页 agent 为主。当前固定 `deepseek-v4-flash` 与 Terminal-Bench 环境不能直接宣称可迁移；先把 folding 指令作为候选 harness 修改，在开发集检验后再决定保留。

## 直接运行

代码与依赖已保存在 [`code/`](code/)，运行时不需要再查论文或 GitHub。`demo` 用确定性的 120 步长程轨迹
跑「不折叠 vs 主动折叠」对比，并检查关键证据在折叠后是否存活，全程不联网、不需要模型：

```bash
cd reproductions/zhouMF/method-reproduction/agentfold-context-folding/code
python3 context_folding.py demo         # 离线自测，输出上下文规模、折叠次数、证据存活
```

真实折叠文本（论文里由训练后的 agent 产生 folding directive）可走 live 路径：

```bash
export OPENAI_API_KEY=...
python3 context_folding.py fold-live --model deepseek/deepseek-v4-flash
```

| 文件 | 用途 |
| --- | --- |
| [`code/context_folding.py`](code/context_folding.py) | 多尺度 workspace、细粒度/深度折叠、折叠策略、证据存活检查、离线 demo、live 入口。 |
| [`code/requirements.txt`](code/requirements.txt) | 依赖清单；核心与自测仅用标准库，live 模式需要 `openai`。 |
| [`code/UPSTREAM.md`](code/UPSTREAM.md) | 上游仓库与固定 revision（完整 deep-research agent，未导入）。 |

## 来源与边界

固定论文与来源见 [source-packet: agentfold-2510.24699](../../../../knowledge/source-packets/agentfold-2510.24699/README.md)；上游代码版本与获取命令见
[code/UPSTREAM.md](code/UPSTREAM.md)。本地 demo 验证的是**折叠策略与证据保留**，不是论文
BrowseComp 的 36.2%；那些是训练后网页 agent 的结果，不能写成本地结果。
