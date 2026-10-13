# 第一阶段配置

- [launch.json](launch.json)：固定 DeepSeek、train 入口、串行、每题 1 次、原生评分时限、优化 2400 秒。
- [deepseek-api.json](deepseek-api.json)：模型接线、思考开启与 socket 时限，不包含凭据。
- [experiment.json](experiment.json)：历史训练条件与来源，保留未知 seed 和原记录。

安装、Docker、预览与显式执行命令见 [运行说明](../README.md)，依赖完整锁定在 `../code-adaptation/requirements-lock.txt`。服务设置与秘密分开保存，通过子进程环境加载。

[H0 历史条件](h0-history.json)对应同一实验的 `../results/h0/summary.json`。
