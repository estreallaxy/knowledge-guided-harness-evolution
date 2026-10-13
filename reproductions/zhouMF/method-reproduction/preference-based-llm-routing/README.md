# Preference-based LLM Routing

## 什么时候使用

需要在强弱模型间动态路由，且拥有目标任务分布上的偏好、质量或成本监督时使用。

## 机制

训练或选择轻量路由器，针对每个请求决定是否升级到强模型，并通过阈值控制质量—成本取舍。

## 本项目边界

原论文的模型对、价格和偏好数据不能直接迁移。当前固定模型协议下仅作为后续资源分配实验候选；如果启用，必须以开发集独立校准并报告路由错误和成本。

## 直接运行

代码与依赖已保存在 [`code/`](code/)，运行时不需要再查论文或 GitHub。`demo` 在合成开发集上跑
门槛校准，比较 always-weak / always-strong / 校准后的路由，全程不联网、不需要模型：

```bash
cd reproductions/zhouMF/method-reproduction/preference-based-llm-routing/code
python3 preference_router.py demo       # 离线自测，输出质量/成本/升级率
```

真实分数与模型（要走 OpenAI 兼容端点，`openai` 已列在 `requirements.txt`）：

```bash
export OPENAI_API_KEY=...
python3 preference_router.py route --request "why does this deadlock" --threshold 0.5
```

| 文件 | 用途 |
| --- | --- |
| [`code/preference_router.py`](code/preference_router.py) | 路由器、开发集校准、策略评估、离线 demo、live 入口。 |
| [`code/requirements.txt`](code/requirements.txt) | 依赖清单；核心与自测仅用标准库，live 模式需要 `openai`。 |
| [`code/UPSTREAM.md`](code/UPSTREAM.md) | 上游仓库与固定 revision。 |

## 来源与边界

固定论文与来源见 [source-packet: routellm-2406.18665](../../../../knowledge/source-packets/routellm-2406.18665/README.md)；上游代码版本与获取命令见
[code/UPSTREAM.md](code/UPSTREAM.md)。本地 demo 验证的是**校准与阈值策略**，
不是论文的成本降低曲线；真实路由器（论文是训练出的偏好分类器）需在开发集上单独训练。
