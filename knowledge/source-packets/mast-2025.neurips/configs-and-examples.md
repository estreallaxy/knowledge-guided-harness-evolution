# Configs and examples

## 运行前提

官方仓库没有 YAML 或配置文件，也没有命令行入口。唯一可执行的流程是 `official-code/llm_judge_pipeline.ipynb`，全部参数硬编码在 notebook 里。运行它需要：

| 前提 | 说明 |
| --- | --- |
| Python 环境 | notebook 记录的 kernelspec 为 `multiagent`（Python 3.11.9）。 |
| OpenAI 客户端与密钥 | `from openai import OpenAI`（`:13`）由 `openai_api_key = "KEY"`（`:16`）占位填充，客户端在 `:17-19` 建立；论文使用的是 o1。 |
| MAST 文本材料 | `taxonomy_definitions_examples/definitions.txt` 与 `examples.txt`，随本来源包提供，notebook 以相对路径读取。 |
| 待标注 trace | notebook 里是 `YOUR_TRACE_FILE.txt` / `YOUR_OTHER_TRACE_FILE.txt` 占位（`:127-131`）；真实 trace 在未纳入的 `traces/` 数据集里。 |

## 官方配置项（硬编码）

| 设置 | 值 | 位置 |
| --- | --- | --- |
| 标注模型 | `model='o1'` | `official-code/llm_judge_pipeline.ipynb:27` |
| 采样温度 | `temperature=1.0` | `official-code/llm_judge_pipeline.ipynb:28` |
| 单条输入上限 | 1,048,570 字符，超出时按 `1048570 - len(examples)` 从尾部截断 | `official-code/llm_judge_pipeline.ipynb:158-159` |
| 断点续跑 | 每条写 `saved_results/o1_results_checkpoint.pkl`，每 10 条另存备份 | `official-code/llm_judge_pipeline.ipynb:165-181` |
| 失败容错 | 单条异常被捕获后继续，并把已有结果落盘 | `official-code/llm_judge_pipeline.ipynb:162-181` |
| 结果分组 | `source_sizes = [30,30,30]`，按固定块长切分后求各来源均值 | `official-code/llm_judge_pipeline.ipynb:305-307` |

notebook 开头还留有 `NousResearch/Meta-Llama-3-8B-Instruct` 与 `base_url="http://localhost:8000/v1"` 的痕迹（`:10-11`，未被后续代码使用）；论文与 Table 2 报告的模型均为 OpenAI o1。

## 官方流程入口

```text
cell 0  (:3-96)     定义 openai_evaluator：trace + MAST 定义 + few-shot 示例 → A 摘要 / B 任务是否完成 / C 十四个模式 yes-no
cell 1  (:98-105)   读取 taxonomy_definitions_examples/examples.txt
cell 4  (:123-133)  装载待标注 trace 列表
cell 6  (:144-182)  逐条调用并落盘断点
cell 8  (:193-282)  parse_responses：把自由文本解析成 14 个模式的 0/1
cell 10 (:301-350)  按 source_sizes 分组汇总各来源失败率
```

最小使用方式（论文 Appendix C，PDF p.28）给出的是库接口，而非本仓库的 notebook：

```python
!pip install agentdash
from agentdash import annotator
MASTAnnotator = annotator("your-api-key")
mast_annotation = MASTAnnotator.produce_taxonomy(trace)
mast_annotation["failure_modes"]      # {模式 id: 是否命中}
MASTAnnotator.get_failure_mode_info("1.1")
mast_annotation["summary"], mast_annotation["task_completion"], mast_annotation["total_failures"]
```

该 `agentdash` 包不在本来源包的代码快照内，本包未做安装或调用验证。

## 数据入口

| 入口 | 位置 | 状态 |
| --- | --- | --- |
| MAST-Data（Hugging Face） | 论文脚注 2（PDF p.1）指向 `https://huggingface.co/datasets/mcemri/MAST-Data` | 论文写法；未下载。 |
| MAD 数据集 | 仓库 `README.md:15-42` 与 `traces/README.md` 指向 `https://huggingface.co/datasets/mcemri/MAD`，含 `MAD_full_dataset.json`（LLM 标注）与 `MAD_human_labelled_dataset.json`（人工标注） | 仓库写法；两处名称与论文脚注不一致，未核实哪一个是当前有效仓库。 |
| 仓库 `traces/` | 上游 HEAD 下共 13359 个文件，分 `AG2`(7184)、`MagenticOne_GAIA`(4535)、`math_interventions`(600)、`HyperAgent`(513)、`programdev`(389)、`mmlu`(91)、`OpenManus_GAIA`(30)、`AppWorld`(16) | 未纳入本来源包。 |
| ProgramDev 任务清单 | `traces/programdev/programdev_dataset.json`（论文 Appendix D 脚注 3 引用该路径） | 未纳入本来源包。 |

## 本地保存范围

已纳入 `official-code/`（13 个文件，893,860 字节 ≈ 0.85 MB）：

| 内容 | 文件 |
| --- | --- |
| 分类法与示例 | `taxonomy_definitions_examples/definitions.txt`、`examples.txt` |
| 标注流水线 | `llm_judge_pipeline.ipynb` |
| 一致性标注原始表 | `inter_annotator_agreement_annotations/` 下 4 个 PDF（合计 272,379 字节） |
| 仓库入口 | `README.md` |
| README 引用的图 | `assets/taxonomy_v11_cropped-1.png`、`taxonomy_v11_cropped.pdf`、`arxiv_figure_v2_cropped-1.png`、`arxiv_figure_v2_cropped.pdf`、`mas22.jpg` |

明确未纳入：

| 未纳入项 | 原因 |
| --- | --- |
| `traces/`（13359 个文件） | 属数据集，且体积远超来源包预算；用上面的 Hugging Face 入口获取。 |
| `assets/mast_logo_with_writing.png`（1.37 MB） | 单个超过 1 MB 的 logo。 |
| 根 `LICENSE` | 上游根目录没有该文件（已核对 HEAD 的树）。 |
| 实验输出、API 密钥 | 仓库内不存在；notebook 中密钥为占位符。 |

快照与上游的一致性已按内容核对：`official-code/` 中 13 个文件的 git blob 哈希与上游 `a70542e541b2104ef8fcd785778179e173fb8d70` 逐一相同，仅剔除了上述 logo。
