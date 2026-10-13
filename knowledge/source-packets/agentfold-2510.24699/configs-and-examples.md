# Configs and examples

以下内容取自 `official-code/`（revision `f72f75d8c3eb842f2bbbab096a12206ff66e270f`），
**未在本机执行**：需要自备 `AgentFold-30B-A3B` 权重与多卡 vLLM 服务。

## 运行前提

| 项目 | 要求 | 来源 |
| --- | --- | --- |
| GPU/服务 | vLLM 多实例（默认 8000–8005 目标模型，8006 `gpt-oss-120b`） | `AgentFold/serve.sh` |
| 模型权重 | 论文的 AgentFold-30B-A3B；**仓库未提供下载地址与权重** | `serve.sh` 中 `MODEL_PATH` 为空 |
| Tokenizer | `AutoTokenizer.from_pretrained("qwen3-30b-a3b")` | `AgentFold/infer.py` |
| 依赖 | 见仓库根 `requirements.txt` | 仓库根 |
| 外部工具 | 搜索/访问工具（`inference/tool_search.py`、`tool_visit.py`），可能需外部检索服务凭据 | `AgentFold/infer.py` 的 sys.path 与 import |
| 评测数据 | BrowseComp、BrowseComp-ZH、WideSearch-en、GAIA | 论文 §5，PDF p.7 |

## 上游示例命令

```bash
# 1) 起模型服务（需先填 MODEL_PATH）
bash AgentFold/serve.sh

# 2) 跑推理（脚本通过 importlib 选择 agent，入口在 AgentFold/infer.py）
python AgentFold/infer.py
```

`serve.sh` 原文（节选）：

```bash
MODEL_PATH=""
MODEL_NAME="all_moreturn_0920"
CUDA_VISIBLE_DEVICES=0 vllm serve ${MODEL_PATH} --host 0.0.0.0 --port 8000 \
  --trust-remote-code --gpu-memory-utilization 0.95 --tensor-parallel-size 1 \
  --served-model-name ${MODEL_NAME} --disable-log-requests &
# …8001–8005 同构；8006 用 gpt-oss-120b（tensor-parallel-size 2）
```

## 未确认项（写为未知）

- `AgentFold/infer.py` 的确切命令行参数：本包未逐一核对 `argparse` 定义与论文设置的对应关系。
- 论文的实验 seed、温度、最大轮数（论文提到 100 轮评测上限与 500 轮扩展）在代码中的默认值。
- 训练侧：SFT 数据构造、超参与训练脚本均不在本快照内。
- 折叠指令的提示词全文：论文有描述，代码中的模板位置需进一步定位（`infer.py` 内的提示拼接）。
