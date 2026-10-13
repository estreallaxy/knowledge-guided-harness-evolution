# Configs and examples

## 论文实验配置

| 设置 | 取值 | 位置 |
| --- | --- | --- |
| Benchmark | WebArena（六个站点：Shop、Admin、Reddit、GitLab、Maps、Multi） | §3.1，PDF p.5 |
| 环境框架 | BrowserGym，观测为 webpage accessibility tree | §3.1，PDF p.5 |
| 动作空间 | WebArena 默认 15 个原语动作 | Appendix A.1，PDF p.14，Table 7 |
| 主干模型 | `claude-3.5-sonnet`，同时用于 agent policy π、评估器 V 与归纳模块 I | §3.1，PDF p.5 |
| 评估器 | 论文自带 program-based evaluator 给 0/1 分 | §3.1，PDF p.5 |
| 基线 | vanilla Claude + BrowserGym；AWM（文本 skill） | §3.1，PDF p.5 |
| 最大步数 | 论文记为 H_max，未给具体数值 | §2.1，PDF p.3 |

**注意**：论文未给出 step 上限、温度、并发、重试与判分超时的具体数值；这些属于 `unknown`，
迁移到本项目时必须自行固定并在结果中说明，不能声称与论文同条件。

## 官方流程入口

论文指向的官方仓库：<https://github.com/zorazrw/agent-skill-induction>
（固定 revision `377abe0623a37eaf7f03bdd26cb97bb5331acf47`）。

```bash
git clone https://github.com/zorazrw/agent-skill-induction.git
git -C agent-skill-induction checkout 377abe0623a37eaf7f03bdd26cb97bb5331acf47
```

快照已入库（revision `377abe0623a37eaf7f03bdd26cb97bb5331acf47`，见 `official-code/`）。
仓库根 README 与运行入口已随快照保存，但本包**未在本机执行**，因此不给出已验证的命令。
运行前需补齐：环境安装、WebArena/BrowserGym 启动方式、诱导与验证脚本入口、评估命令；
`official-code/asi/` 下的入口可直接从仓库根 README 与 `asi/run_demo.py` 入手阅读。

## 论文中的可复制片段

Table 7（PDF p.14）列出全部原语动作，可直接作为动作空间对照表：

```
noop(wait_ms)  click(elem)  hover(elem)  fill(elem, value)
keyboard_press(key_comb)  scroll(x, y)  select_option(elem, options)
goto(url)  go_back()  go_forward()  new_tab()  tab_close()
tab_focus(index)  send_msg_to_user(text)  report_infeasible(reason)
```

三个 LM 组件（episode 评估、episode 清洗、skill induction）的提示词全文在
Appendix A.2（PDF pp.14–16），迁移时可先用论文提示词打通流程，再用官方代码核对差异。

## 本地保存范围

当前只保存论文 PDF 与全文文本。`official-code/`、WebArena/BrowserGym 环境、
WebArena 任务数据与运行缓存均未纳入。

