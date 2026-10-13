# Frugal LLM Cascade

## 什么时候使用

多个模型或近似器可用，且可以在质量、费用与延迟之间做显式权衡时使用。

## 机制

对不同请求学习模型组合或级联策略：先用低成本路径，只有当置信度/条件不足时才升级到高成本模型。

## 本项目边界

当前复现协议固定执行模型与优化模型，因此本方法暂不改变 H0。只有共同协议允许多模型后，才能在开发集重新校准成本、延迟、质量阈值和失败回退。

## 直接运行

代码与依赖已保存在 [`code/`](code/)，运行时不需要再查论文或 GitHub。`demo` 用三个合成模型和
100 条确定性开发查询做门槛校准，比较 always-small / always-large 与校准后的级联，全程不联网：

```bash
cd reproductions/zhouMF/method-reproduction/frugal-llm-cascade/code
python3 cascade_router.py demo          # 离线自测，输出质量/成本/升级率与误设门槛的代价
```

真实模型级联（要走 OpenAI 兼容端点，`openai` 已列在 `requirements.txt`）：

```bash
export OPENAI_API_KEY=...
python3 cascade_router.py run-live --query "explain this stack trace" \
  --models small-model,large-model --tau 0.6
```

| 文件 | 用途 |
| --- | --- |
| [`code/cascade_router.py`](code/cascade_router.py) | 级联执行、门槛校准、成本/质量评估、离线 demo、live 入口。 |
| [`code/requirements.txt`](code/requirements.txt) | 依赖清单；核心与自测仅用标准库，live 模式需要 `openai`。 |
| [`code/UPSTREAM.md`](code/UPSTREAM.md) | 上游仓库与固定 revision。 |

## 来源与边界

固定论文与来源见 [source-packet: frugalgpt-2305.05176](../../../../knowledge/source-packets/frugalgpt-2305.05176/README.md)；上游代码版本与获取命令见
[code/UPSTREAM.md](code/UPSTREAM.md)。本地 demo 验证的是**门槛校准机制**，不是论文的 GPT-3/3.5/4
成本节省曲线；真实打分函数需要按论文训练，本地用确定性置信度占位。
