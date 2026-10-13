# Configs and examples

上游仓库没有 YAML/JSON 形式的实验配置文件，也没有 `requirements.txt`、`setup.py` 或 `pyproject.toml`。可复现的「配置」只有四处：CLI 参数、数据集目录映射、评测集规模表，以及各数据集的指令字符串。以下配置只能与固定论文版本、固定代码 revision 和未纳入本包的数据集一起解释；论文中的运行结果不能由本目录的任何单个文件独立复现。

## 官方实验配置

| 设置 | 配置位置 | 主要差异 |
| --- | --- | --- |
| 被评估模型 | `official-code/generate/generate_loop.py:556`（`--model`）、`official-code/utils/chat.py:103-110` | 代码接受 `vicuna`、`sft`、含 `chatgpt` 的字符串并硬编码为 `gpt-3.5-turbo-1106`；其余取值抛 `ValueError`。 |
| 生成方法 | `official-code/generate/generate_loop.py:559,567`（`--method`） | 取值 `plan_retrieve` / `task_retrieve` / `select` / `dfs` / `rewrite`，对应论文 §4 的五个方法。 |
| 数据集与目录映射 | `official-code/generate/dataset_path_dict.py:10-35` | 24 个键（19 个 `wikihow-<类别>` + `tools-APIBank` / `tools-GPT4Tools` / `tools-ToolAlpaca` + `robot-VirtualHome` / `robot-saycan`），指向 `wikihow_500/`、`tools_500/`、`robot_500/`。生成与评测两侧共用这套命名。 |
| 评测集规模（指标分母） | `official-code/evaluate/eval_set_size.json` | 每个 wikiHow 类别 500、GPT4Tools 500、VirtualHome 500；APIBank 263、ToolAlpaca 201、robot-saycan 164。分母固定，与 `eval_fast` 无关。 |
| 各数据集的提示词与 few-shot | `official-code/generate/dataset_settings/base_dataset.py:35-116`（共用）、`wikihow.py:18-39`、`apibank.py:16-32`、`gpt4tools.py:16-32`、`toolalpaca.py:24-42`、`saycan.py:19-39`、`virtualhome.py:17-37`（子集覆盖） | 三个工具类数据集把初始计划 `init_plan_instruction` 覆盖为「api name + `DESCRIPTION:` + 注释」的格式；其余子集沿用基类，只在 few-shot 例子上不同。 |
| 召回数量与迭代上限 | 论文 Appendix B（PDF p.12）；代码 `generate_loop.py:103,150,233,358,471,77-79,191,313,436` | 论文：Plan-Retrieve 每步 2、Task-Retrieve 20、Select/DFS 5、Rewrite 每步约 10；迭代上限 20/30/20。代码与论文在 Rewrite 召回数上不一致（代码为 10/5/4 三档，见 `exact-source-anchors.md`）。 |

## 官方流程入口

官方仓库把过程分为三步：

1. `utils/embedding.py`：为每个数据集的动作库生成嵌入，保存为 `actions_emb.npy` 放进对应数据集目录（上游 `README.upstream.md:15`）。仓库不上传嵌入文件。
2. `generate/generate_loop.py`：按方法生成计划，逐任务写 `json` 记录与 `<predict_path>_chat/` 对话日志。
3. `evaluate/evaluate.py` + `evaluate/get_score_result.py`：对生成结果做 ChatGPT 成对评判并汇总。

### 生成

必须在仓库根目录运行（脚本依赖 `generate.dataset_settings.*` 与 `utils.*` 包路径），并先修改 `generate_loop.py:23` 的 `sys.path.append(...)` 与 `:563-564` 的 `source_path` / `predict_path`：

```bash
# 在仓库根目录、已改好硬编码路径之后
python generate/generate_loop.py \
        --model chatgpt \
        --dataset "wikihow-Computers and Electronics" \
        --method rewrite \
        --version final_eval \
        --max_workers 8
```

`--dataset` 取 `generate/dataset_path_dict.py` 中的 24 个键之一；`--method` 取五个方法之一。

### 评测

必须在 `evaluate/` 目录内运行（`evaluate.py:11` 与 `eval_utils.py:11` 用 `sys.path.append("..")`，且 `eval_utils.py:61` 以相对路径读 `./eval_set_size.json`），并先把生成结果路径填进 `evaluate.py:17` 的 `eval_records_dir`：

```bash
cd evaluate
python evaluate.py \
        --eval_model chatgpt \
        --baseline_method rewrite \
        --version final_eval \
        --eval_set_type wikihow \
        --eval_fast False
```

`official-code/evaluate/eval.sh:2-7` 是同一命令的官方写法。`--eval_set_type` 取 `wikihow` / `tools` / `robot`；`--eval_fast` 传字符串 `True` / `False`（只有字面 `"True"` 才触发前 100 例快评）。

### 汇总

```bash
cd evaluate
python get_score_result.py      # 编辑 :32-47 的 eval_result_dir_list 以指定要汇总的结果目录
```

## 运行前需要自备的外部依赖

| 依赖 | 说明 |
| --- | --- |
| 数据集 | 上游 `datasets/`（24 个数据集目录，各含 `tasks.json` + `actions.txt`，另有 `_full` 全集）未纳入本包。 |
| 动作嵌入 | 每个数据集目录需要一份 `actions_emb.npy`（`generate_loop.py:40,45` 直接 `np.load`），需用 `utils/embedding.py` + 自己的 OpenAI key 生成。 |
| OpenAI 兼容端点与密钥 | `utils/chat.py:20-32` 与 `utils/embedding.py:13-16` 的 `api_key` / `base_url` 均为空字符串；评测侧同样走 OpenAI 兼容接口。 |
| Python 包 | 无 requirements 文件；由 import 可推出需要 `openai`、`tenacity`、`tqdm`、`faiss`（CPU 版即可，用的是 `IndexFlatIP`）、`numpy`、`matplotlib`。 |

## 本地保存范围

`official-code/` 保存的是上游 `generate/`、`evaluate/`、`utils/` 三个目录的全部源码，加上根目录的 `readme.md`（在本包中改名为 `README.upstream.md` 以免与包自身 README 混淆）与 `.gitignore`，共 22 个文件、约 140 KB —— 即上游除数据集以外的全部代码。

**没有纳入**的内容：

- 上游 `datasets/` 目录：24 个数据集 × (`tasks.json` + `actions.txt`)，另有 `wikihow_full` / `tools_full` / `robot_full` 全集，是仓库体积的主要来源（GitHub 报仓库约 21 MB）。属于「数据集」，按规范剔除。
- 预计算的 `actions_emb.npy` 嵌入文件：上游本身也未上传。
- `predict/`、`predict_chat/`、`eval_results/` 等运行产物与缓存：上游 `.gitignore` 只忽略 `.idea`，这些目录不存在于仓库中。
- 微调 LLaMA-2-7B(SFT) 的训练代码与数据：论文 §5.1 说明用 FastChat 训练，但仓库中**没有**对应的训练脚本；这部分无法从本包复现（未知）。
- 任何 API key。
