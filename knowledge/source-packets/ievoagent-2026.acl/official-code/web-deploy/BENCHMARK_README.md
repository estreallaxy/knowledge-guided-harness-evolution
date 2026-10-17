# 对话延时基准测试 (vLLM / GPT-4o / IEvoAgent)

## 概述

`benchmark_latency.py` **按基座模型分类**测量对话延时：每个用户有 4 个 task，每个 task 对应一个 `assignedModel`（IEvoAgent / kto / GPT-4o / qwen2.5）。脚本只对「该 task 的 assignedModel」测量该 task 下各轮对话的回复延时，即：

- **IEvoAgent**：只测 `assignedModel=IEvoAgent` 的 task 中的轮次
- **kto**：只测 `assignedModel=kto` 的 task 中的轮次
- **GPT-4o**：只测 `assignedModel=GPT-4o` 的 task 中的轮次
- **qwen2.5**：只测 `assignedModel=qwen2.5` 的 task 中的轮次

这样得到的是每个基座模型在实验中实际负责的那部分对话的延时统计。

## 安装依赖

```bash
# 确保已安装 openai 和 aiohttp（用于 IEvoAgent）
pip install openai aiohttp
```

## 使用方法

### 1. 启动 vLLM 服务

在运行基准测试前，需启动 vLLM 服务：

```bash
cd ./web-deploy/backend
bash vllm_start.sh  # 或按需手动启动两个 vLLM 实例（端口 8009, 8010）
```

### 2. 启动后端服务（用于 IEvoAgent）

```bash
cd ./web-deploy/backend
python server.py
```

### 3. 运行基准测试

#### 完整测试（全部 4 个模型，全部 24 用户）

```bash
cd ./web-deploy
python benchmark_latency.py --save-details
```

#### 快速测试（前 2 个用户，每任务前 3 轮）

```bash
python benchmark_latency.py --max-users 2 --max-turns 3
```

#### 只测试 vLLM 模型（跳过 GPT-4o 和 IEvoAgent）

```bash
python benchmark_latency.py --models qwen2.5 kto
```

#### 只测试 qwen2.5 和 kto（不需要后端）

```bash
python benchmark_latency.py --models qwen2.5 kto
```

### 4. 查看结果

运行完成后，会生成：
- `latency_summary.json`: 各模型的延时汇总统计（mean, median, p95 等）
- `latency_details_*.json` (如果使用 `--save-details`): 每轮详细延时

示例输出：
```
========== 对话延时汇总 (秒) ==========
  qwen2.5: mean=1.234s, median=1.123s, p95=2.456s, n=480
  kto: mean=1.345s, median=1.234s, p95=2.567s, n=480
  GPT-4o: mean=2.123s, median=1.987s, p95=3.456s, n=480
  IEvoAgent: mean=3.456s, median=3.123s, p95=5.678s, n=480
```

## 常用参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--results-dir` | IEVO-*_Result.json 所在目录 | `./results` |
| `--models` | 要测试的模型（可多选） | `GPT-4o qwen2.5 kto IEvoAgent` |
| `--max-users` | 最多使用前 N 个用户 | 全部 |
| `--max-turns` | 每个任务最多取前 N 轮 | 全部 |
| `--max-samples` | 总样本数上限 | 无限制 |
| `--max-tokens` | 单次生成 max_tokens | 1024 |
| `--save-details` | 保存每轮详细延时到 JSON | False |
| `--openai-api-key` | OpenAI API Key | 从环境变量 `OPENAI_API_KEY` |
| `--backend-url` | IEvoAgent 后端 base URL | `http://localhost:8000` |
| `--fail-fast` | 任一请求失败即退出 | False |

## 环境变量配置

可通过环境变量覆盖默认配置：

```bash
export BENCH_RESULTS_DIR=/path/to/results
export OPENAI_API_KEY=sk-...
export BASE_VLLM_API_URL=http://localhost:8009/v1
export KTO_VLLM_API_URL=http://localhost:8010/v1
export IEVO_BACKEND_URL=http://localhost:8000
```

## 注意事项

1. **GPT-4o**: 需要有效的 OpenAI API Key（通过 `--openai-api-key` 或环境变量 `OPENAI_API_KEY`）
2. **qwen2.5 / kto**: 需要 vLLM 服务运行在指定端口（8009, 8010）
3. **IEvoAgent**: 需要后端服务 (`server.py`) 运行在 `http://localhost:8000`
4. 延时测量包含网络往返时间 (RTT)，建议在本地或低延时环境运行以获得准确结果
5. IEvoAgent 的延时包含 agent 逻辑（工具调用、推理等），通常比直接 vLLM 慢

## 常见问题

**Q: 如何跳过 IEvoAgent 测试？**  
A: 使用 `--models` 参数只选择需要的模型：
```bash
python benchmark_latency.py --models qwen2.5 kto GPT-4o
```

**Q: 测试时间过长怎么办？**  
A: 使用 `--max-users` 和 `--max-turns` 限制样本数：
```bash
python benchmark_latency.py --max-users 5 --max-turns 3
```

**Q: vLLM 连接失败？**  
A: 检查 vLLM 服务是否启动：
```bash
ps aux | grep vllm
curl http://localhost:8009/v1/models  # 应返回模型列表
```

**Q: 如何测量 TTFT (Time To First Token)？**  
A: 当前脚本测量的是完整生成延时 (end-to-end)。如需 TTFT，需修改脚本使用流式 API (`stream=True`) 并记录首 token 时间。

## 示例：完整流程

```bash
# 1. 启动 vLLM（两个实例）
cd ./web-deploy/backend
bash vllm_start.sh &

# 2. 启动后端
python server.py &

# 3. 运行基准测试
cd ..
python benchmark_latency.py --save-details --max-users 10

# 4. 查看结果
cat latency_summary.json
```
