# Configs and examples

以下内容取自 `official-code/README.md` 与 `config.example.yaml`（revision
`0b64fdafe049e596a3f5657c219329f24af24198`），**未在本机执行**。

## 运行前提

| 项目 | 要求 | 来源 |
| --- | --- | --- |
| 安装 | `pip install "routellm[serve,eval]"` 或源码 `pip install -e .[serve,eval]` | 上游 README Installation |
| 强/弱模型凭据 | 论文用 `gpt-4-1106-preview` + `Mixtral-8x7B-Instruct-v0.1`（Anyscale 托管） | 上游 README Quickstart；论文 §5.1 |
| 路由器权重 | HuggingFace 上的 `routellm/*` checkpoint（`mf_gpt4_augmented` 等） | `config.example.yaml` |
| 训练数据 | Chatbot Arena 人类偏好对战（`lmsys/lmsys-arena-human-preference-55k`）、GPT-4 judge battles | `config.example.yaml` |
| 校准数据 | 按查询分布校准阈值（论文用 Arena 数据） | 上游 README Threshold Calibration |

## 上游示例命令

```bash
# 1) 用控制器做 drop-in 替换（Python SDK）
python - <<'PY'
import os
from routellm.controller import Controller
os.environ["OPENAI_API_KEY"] = "sk-XXXXXX"
os.environ["ANYSCALE_API_KEY"] = "esecret_XXXXXX"
client = Controller(routers=["mf"], strong_model="gpt-4-1106-preview",
                    weak_model="anyscale/mistralai/Mixtral-8x7B-Instruct-v0.1")
PY

# 2) 校准阈值：让约 50% 的请求走强模型
python -m routellm.calibrate_threshold --routers mf --strong-model-pct 0.5 --config config.example.yaml
# 上游输出示例：For 50.0% strong model calls for mf, threshold = 0.11593

# 3) 生成时用 router-<name>-<threshold> 指定路由器
#    model="router-mf-0.11593"

# 4) 或用 OpenAI 兼容服务
python -m routellm.openai_server --routers mf --strong-model gpt-4-1106-preview \
  --weak-model anyscale/mistralai/Mixtral-8x7B-Instruct-v0.1
```

## 配置片段

```yaml
# config.example.yaml（节选）
sw_ranking:
    arena_battle_datasets:
      - lmsys/lmsys-arena-human-preference-55k
      - routellm/gpt4_judge_battles
causal_llm:
    checkpoint_path: routellm/causal_llm_gpt4_augmented
bert:
    checkpoint_path: routellm/bert_gpt4_augmented
mf:
    checkpoint_path: routellm/mf_gpt4_augmented
```

## 未确认项（写为未知）

- 四个路由器各自的确切超参（除论文写明的缩放系数 γ = 10 外）：未逐一核对。
- 论文 Table 1–4 与 `routellm/evals/` 脚本的对应命令：评测代码已纳入，底层第三方数据集（GSM8K/MMLU/MT-Bench）需自行获取。
- 「>40% cheaper than commercial offerings」的比较对象与调用方式：论文放在附录 E，本包未转录。
