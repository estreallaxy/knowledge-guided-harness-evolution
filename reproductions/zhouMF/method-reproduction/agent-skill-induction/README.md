# Agent Skill Induction

## 什么时候使用

用于任务重复出现、可安全探索环境，并且希望把经验证的多步操作固化为可执行 Skill 的场景。

## 机制

1. 在开发任务中交互并提出候选程序化 Skill。
2. 通过可执行验证检查 Skill 是否满足其声明。
3. 以描述和程序共同保存，通过检索复用；站点或环境变化时重新验证或更新。

## 本项目边界

ASI 依赖 WebArena 与浏览器执行环境，不能直接接入当前 Terminal-Bench H0。若迁移，必须隔离开发任务、保留验证证据，且禁止把封存测试结果写入 Skill。

## 直接运行

代码与依赖已保存在 [`code/`](code/)，运行时不需要再查论文或 GitHub。`demo` 用确定性的最小 Web 环境
跑完整的「诱导 → 执行式验证 → 复用」链路，并复现论文强调的假成功消融，全程不联网、不需要模型：

```bash
cd reproductions/zhouMF/method-reproduction/agent-skill-induction/code
python3 skill_induction.py demo        # 离线自测，11 行输出 + self-test OK
```

需要真实模型提议程序时（要走 OpenAI 兼容端点，`openai` 已列在 `requirements.txt`）：

```bash
export OPENAI_API_KEY=...              # 或用 DEEPSEEK_API_KEY + OPENAI_BASE_URL
python3 skill_induction.py induce-live --goal "submit the item rating"
```

| 文件 | 用途 |
| --- | --- |
| [`code/skill_induction.py`](code/skill_induction.py) | 最小 Web 环境、诱导、执行式验证、Skill 库与检索、离线 demo、live 入口。 |
| [`code/requirements.txt`](code/requirements.txt) | 依赖清单；核心与自测仅用标准库，live 模式需要 `openai`。 |
| [`code/UPSTREAM.md`](code/UPSTREAM.md) | 上游仓库与固定 revision（WebArena/BrowserGym 版，未导入）。 |

## 来源与边界

固定论文与来源见 [source-packet: agent-skill-induction-2504.06821](../../../../knowledge/source-packets/agent-skill-induction-2504.06821/README.md)；上游代码版本与获取命令见
[code/UPSTREAM.md](code/UPSTREAM.md)。本地 demo 验证的是**机制**，不是论文的 WebArena 分数：
上游依赖 BrowserGym/WebArena，本项目没有迁移，也不把 WebArena 结果写成本地结果。
