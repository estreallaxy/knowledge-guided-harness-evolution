# 李嘉旺：复现与论文收集

| 项目 | 安排 |
| --- | --- |
| 服务器账号 | `liJW`；VS Code SSH 主机 `gpu-liJW`，端口 `30056`。密码见本地 `other/server_ssh_accounts.md`，不写入仓库。 |
| 专属目录 | `/data1/users/liJW/`，归本人所有；已加入 `docker` 组，并以本人账号验证 Docker daemon 可访问。 |
| 开发分支 | `liJW/self-evolution-branch`，从远端 `main` 创建。 |
| 复现代码 | `reproductions/liJW/meta-harness/code/`；独立复制仓库中已导入的官方 Meta-Harness 代码快照，无嵌套 `.git`。 |
| 运行模型 | 执行与优化模型均为 `deepseek-v4-flash`。个人配置、环境、缓存和结果自行维护，不引用其他成员目录。 |
| 共同评测 | 仓库根目录 `benchmarks/terminal-bench-2.0/`，同一 `split-v1.json`，具体字段见 `experiments/configs/README.md`。 |
| GitHub 认证 | 需提供本人 GitHub 用户名以邀请协作者，并在本人 Linux 账号配置自己的 GitHub SSH 密钥；不复用其他成员凭据。 |
| 当前状态 | 服务器账号、密码登录、目录和 Docker 权限已验证。个人目录中未克隆仓库；未运行模型或 benchmark。 |

| 论文方向 | 现有参考 | 后续任务 |
| --- | --- | --- |
| 规划与任务进度管理 | LLM+P | 阅读现有材料，再补充一篇；核对机制、适用条件与实现。 |
| 权限、审批与运行隔离 | CaMeL | 阅读现有材料，再补充一篇；区分信息流控制、审批与环境隔离。 |
| 验证、评估与反馈 | CRITIC | 阅读现有材料，再补充一篇；区分执行时纠错与 Harness 优化时评测。 |

每方向累计两篇。原文进入 `knowledge/sources/<id>/`，方法描述与证据进入 `knowledge/methods/<id>/`，实现进入该方法的 `implementations/<impl-id>/files/`。按当前知识组织规范校验，链接与进度同步到研究计划 2.1。既有条目由新负责人接续，不重复新建。
