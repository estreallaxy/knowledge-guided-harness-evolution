# Plan-and-Solve Prompting

## 什么时候使用

任务可在行动前拆成相对稳定的子目标，且当前失败主要来自漏步骤而不是环境状态快速变化时使用。

## 机制

先生成完整计划，再按子任务执行；PS+ 额外要求提取变量和中间信息，以减少遗漏与计算错误。

## 本项目边界

原论文是静态推理任务。工具型 agent 使用时必须把计划看作可修订状态，不能因初始计划而忽略新的环境反馈或 verifier 结果。

## 直接运行

代码与依赖已保存在 [`code/`](code/)，运行时不需要再查论文或 GitHub，也不需要装第三方包。`demo`
用脚本化的 `ScriptedClient` 跑通「构建提示 → 取回文本 → 还原 plan → 抽取答案」，覆盖 cot / ps / ps+
三个变体，全程不联网、不需要模型：

```bash
cd reproductions/zhouMF/method-reproduction/plan-and-solve-prompting/code
python3 plan_and_solve.py demo          # 离线自测，输出各变体的计划步数与答案
```

真实模型（要走 OpenAI 兼容端点，`openai` 已列在 `requirements.txt`）：

```bash
export OPENAI_API_KEY=...
python3 plan_and_solve.py solve-live --question "Natalia sold clips to 48 friends in April, ..." \
  --variant ps+ --model deepseek/deepseek-v4-flash
```

| 文件 | 用途 |
| --- | --- |
| [`code/plan_and_solve.py`](code/plan_and_solve.py) | 论文原样提示串、提示构建、plan/execution 切分、答案抽取、`ModelClient` 协议、离线 demo 与 live 入口。 |
| [`code/requirements.txt`](code/requirements.txt) | 依赖清单；核心与自测仅用标准库，live 模式需要 `openai`。 |
| [`code/upstream/`](code/upstream/) | 上游**部分**快照（`prompt.py` 等），仅作来源与提示串出处，不被导入；其自带 README 引用的图片未包含。 |
| [`code/UPSTREAM.md`](code/UPSTREAM.md) | 上游仓库与固定 revision。 |

## 来源与边界

固定论文与来源见 [arXiv:2305.04091](https://arxiv.org/abs/2305.04091)（该论文不在本人负责的来源包范围内）；
上游代码版本与获取命令见
[code/UPSTREAM.md](code/UPSTREAM.md)。本地 demo 验证的是**提示与解析链路**，不是论文的准确率提升：
推理质量取决于执行模型，论文只报告静态多步推理数据集上的结果，本项目尚未做该对照。
