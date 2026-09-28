# GitHub 协作手册

本仓库为私有仓库。`main` 保存共同协议和已审阅的稳定版本；日常开发在各自分支进行。研究规划见 [docs/research-plan.md](docs/research-plan.md)。以下命令在**各自 Linux 账号下的仓库目录**执行。

| 成员 | Linux 账号 | 开发分支 | 专属工作区 |
| --- | --- | --- | --- |
| 周梦凡 | `zhouMF` | `zhouMF/self-evolution-branch` | `/data1/users/zhouMF` |
| 赵星源 | `zhaoXY` | `zhaoXY/self-evolution-branch` | `/data1/users/zhaoXY` |
| 王懿 | `wangY` | `wangY/self-evolution-branch` | `/data1/users/wangY` |

三个 Linux 账号和工作区已分别创建，且可以使用各自账号进行密码 SSH 登录。首次克隆私有仓库前，还需为每个人配置 GitHub 账号协作者权限和 GitHub SSH 认证。准备就绪后，在自己的工作区克隆对应分支，例如周梦凡：

```bash
cd /data1/users/zhouMF
git clone --branch zhouMF/self-evolution-branch git@github.com:estreallaxy/knowledge-guided-harness-evolution.git
cd knowledge-guided-harness-evolution
```

首次提交前，在**自己的仓库目录**设置真实的 Git 提交身份；勿修改全局配置：

```bash
git config user.name "你的姓名或 GitHub 用户名"
git config user.email "你在 GitHub 验证过的邮箱"
```

**Git 提交作者、推送时认证的 GitHub 账号和 PR 作者不是一回事**：提交邮箱须关联本人 GitHub 账号；Git 拉取和推送使用本人 SSH 密钥；PR 用本人 GitHub 账号发起和审阅。

## 每次开始开发

先保存或提交自己尚未提交的改动，再同步 `main` 和自己的分支。以下以周梦凡的分支为例；另外两位把分支名换成上表中的名字。

```bash
git status
git fetch origin
git switch main
git pull --ff-only origin main
git switch zhouMF/self-evolution-branch
git pull --rebase origin zhouMF/self-evolution-branch
git rebase main
```

`git pull --ff-only` 保证本地 `main` 不产生意外合并提交。`git rebase main` 把自己的开发提交放到最新 `main` 之后；如果暂时没有个人提交，它只会更新分支起点。同步后再开始修改代码。

## 开发和推送

- 一次改动尽量只解决一件事；共享的 `H0`、benchmark 划分、评分器接口或预算协议发生变化时，在 PR 中说明对现有实验的影响。
- 提交代码、轻量配置和必要文档；不要提交密码、密钥、`.env`、测试题答案、原始数据集、大体积 trace 或运行产物。
- 提交前运行与改动相应的检查，并在 PR 里写清命令和结果；尚未跑通的实验明确标记。

```bash
git status
git add <你修改的文件>
git commit -m "简短描述本次改动"
git push origin HEAD
```

`git add` 建议点名文件，避免把本地实验产物一起提交。不要直接向 `main` 推送开发提交。

## 合并前：rebase、PR、审阅

准备合并时重新同步 `main`，并把自己的分支 rebase 到它的最新提交之后：

```bash
git fetch origin
git switch main
git pull --ff-only origin main
git switch zhouMF/self-evolution-branch
git rebase main
git push --force-with-lease origin HEAD
```

`rebase` 会改写自己分支的提交历史，所以已推送过该分支时使用 `--force-with-lease` 更新；**只对本人负责的分支使用，不对 `main` 使用，也不要用普通的 `--force`**。如果别人也在同一分支提交过内容，先沟通并核对远端提交，再决定如何同步。

随后在 GitHub 创建以 `main` 为目标、以自己分支为来源的 PR。PR 至少说明：改动目的、主要文件或机制、验证命令与结果；涉及实验时注明 `H0`、模型、数据划分、预算和结果路径。PR 统一由 `zhangXY` 审阅，通过检查并处理意见后再合并。已有 PR 经 rebase 推送后会自动更新，无需另建 PR。

遇到 rebase 冲突时：

```bash
git status
# 手动解决冲突，然后逐个 git add 已解决的文件
git rebase --continue
# 如果需要撤销本次 rebase：git rebase --abort
```

不要通过丢弃不理解的改动来消除冲突；涉及共同实验协议时先与相关成员确认。合并后，下次开发仍从“每次开始开发”的同步步骤做起。
