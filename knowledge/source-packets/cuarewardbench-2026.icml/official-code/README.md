# CUA Reward Bench

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License: Apache 2.0"></a>
  <img src="https://img.shields.io/badge/python-3.8%2B-blue.svg" alt="Python 3.8+">
</p>

<p align="center"><strong>A Comprehensive Benchmark for Evaluating Computer User Agents with Reward Models</strong></p>

## 📋 Overview

**CUARewardBench** is the first comprehensive benchmark for evaluating reward models on Computer-Using Agent (CUA) tasks. While script-based verifiers are widely adopted for CUA evaluation, they suffer from limited scalability and inability to provide step-wise assessment. Reward models offer promising alternatives, but their effectiveness on CUA evaluation remains largely underexplored.

CUARewardBench addresses this gap with four key contributions:

- 🎯 **First-ever Comprehensive CUA Reward Benchmark:** Systematic evaluation framework for both Outcome Reward Models (ORM) and Process Reward Models (PRM) on CUA tasks, enabling trajectory-level and step-level assessment.
- 📊 **Diverse, Practical and Reliable Dataset:** Encompasses trajectories from 10 software categories and 7 agent architectures with varying performance levels (25.9%–50.8% success rates). All trajectories are expertly annotated through carefully designed protocols with rigorous quality control.
- 🔍 **Comprehensive Analysis and Insights:** Extensive experiments across 7 vision-language models and 3 prompt templates reveal critical limitations of current CUA reward models, including insufficient visual reasoning capabilities, knowledge deficiencies, and the superiority of general VLMs over specialized CUA models.
- 🚀 **Unanimous Prompt Ensemble (UPE):** A novel ensemble method that significantly enhances reward model reliability through strict unanimous voting and strategic prompt-template configurations, achieving 88.0% precision and 95.3% NPV for ORM, and 83.1% precision and 86.2% NPV for PRM.

<p align="center">
  <img src="docs/assets/upe_performance.svg" alt="UPE achieves superior reward model reliability" width="100%">
</p>

**Figure 1. UPE achieves superior reward model reliability.** Performance comparison on ORM and PRM tasks shows that our proposed UPE (red star) simultaneously achieves high precision and NPV, significantly outperforming single VLMs with different prompts and traditional ensemble methods (majority-voting). The upper-right positioning demonstrates UPE’s effectiveness in balancing positive and negative prediction accuracy. Details of UPE are discussed in Section 3.5.

## Repository Layout

```text
CUARewardBench/
├── README.md
├── pyproject.toml
├── requirements.txt
├── .env.example
├── LICENSE
├── CITATION.cff
├── configs/
│   ├── prompts/                     # Prompt templates
│   ├── models.example.yaml          # Public-facing model config example
│   └── voting.example.yaml          # Public-facing voting config example
├── cuarewardbench/
│   ├── cli/
│   │   ├── eval_benchmark.py        # Benchmark evaluation entry
│   │   ├── eval_trajectory.py       # Agent trajectory evaluation entry
│   │   ├── vote.py                  # UPE / voting entry
│   │   └── export_excel.py          # Metrics JSON -> Excel utility
│   └── core/
│       ├── config.py                # Registry and default paths
│       ├── data_io.py               # Data loading and result file management
│       ├── llm_eval.py              # Multimodal LLM/RM API wrapper
│       ├── metrics_calculator.py    # Metrics computation and Excel export
│       ├── model_config.py          # Public-safe model registry using env/CLI overrides
│       ├── result_parser.py         # LLM output parser
│       └── utils.py                 # Compatibility re-export layer
├── data/
│   ├── README.md
│   ├── annotations/
│   │   └── cuarewardbench-v0.4.json
│   ├── trajectories/                # Populated locally after `bash scripts/download_data.sh`
│   │   └── osworld_verified/        # Default benchmark data location
│   └── manifest.jsonl               # Checksums for data verification
├── scripts/
│   ├── run_eval_cuarewardbench.sh
│   ├── run_eval_trajectories.sh
│   ├── reproduce_qwen3vl32b_final.sh
│   ├── reproduce_qwen3vl32b_v2prompt.sh
│   ├── download_data.sh
│   ├── prepare_downloaded_trajs.py
│   ├── prepare_manifest.py
│   └── verify_data.py
├── docs/
│   ├── dataset_card.md
│   ├── annotation_protocol.md
│   ├── data_format.md
│   ├── model_api.md
│   └── reproduction.md
├── tests/                           # Regression tests and future smoke checks
└── outputs/                         # Generated results; ignored by git
```

## Installation

```bash
cd CUARewardBench
python3 -m pip install -e .
```

Or install the minimal requirements directly:

```bash
python3 -m pip install -r requirements.txt
```

Optional dependencies:

- `openpyxl`: required for Excel export.
- `pillow`: required when `--img_scale` is not `1.0`.
- `anthropic`: required only for `api_type=claude`.
- `openai`: required for native OpenAI client modes; OpenAI-compatible HTTP mode can use `requests`.

## Data

### Default Layout

The benchmark expects the following data layout:

```text
data/
├── annotations/
│   └── cuarewardbench-v0.4.json
└── trajectories/
    └── osworld_verified/
        └── {model_setting}/{task_type}/{task_id}/
            ├── traj.jsonl
            ├── step_1.png
            ├── step_2.png
            └── ...
```

`cuarewardbench-v0.4.json` contains trajectory-level labels and step-level annotations. The trajectory root contains screenshots and action traces.

### Public Release Data Policy

Trajectory screenshots/images are not redistributed in this repository. The public release workflow downloads the original upstream archives and normalizes them locally:

1. Download raw trajectory archives with `scripts/download_data.sh`.
2. Normalize downloaded archives with `scripts/prepare_downloaded_trajs.py`.
3. Verify the normalized tree against `data/manifest.jsonl` with `scripts/verify_data.py`.
4. Materialize the verified tree into the real repository data directory `data/trajectories/osworld_verified/`.
5. Run benchmark evaluation only after verification succeeds.

By default, `scripts/download_data.sh` keeps bulky raw/prepared cache files in the sibling workspace `../data_build_workspace/` and then copies the verified benchmark tree into `data/trajectories/osworld_verified/`.

```bash
# Full download + normalize + size/sha256 verification
bash scripts/download_data.sh

# Reuse downloaded archives/extracted files during iteration
SKIP_DOWNLOAD=1 SKIP_EXTRACT=1 bash scripts/download_data.sh

# Verify the prepared cache explicitly if needed
python3 scripts/verify_data.py \
  --trajectory_root ../data_build_workspace/prepared/osworld_verified

# The repository benchmark layout is materialized automatically at:
# data/trajectories/osworld_verified
```

If raw archives contain multiple trials for the same task, `prepare_downloaded_trajs.py` selects only the candidate that exactly matches `data/manifest.jsonl`; unmatched cases fail fast instead of guessing. For the observed `uitars15-7b-15step` archive, the script deterministically regenerates missing `traj_tran.jsonl` files from `traj.jsonl` and accepts them only when the generated bytes match the manifest checksum.

Related docs:

- `docs/dataset_card.md`
- `docs/data_format.md`
- `docs/reproduction.md`

The upstream source revision used during preparation is pinned in `../data_build_workspace/source_archives.json` after you run the download workflow.

## Model Configuration

Model configs are loaded from `cuarewardbench/core/model_config.py`. The registry keeps the historical config names used by existing scripts, but it is public-safe by default: credentials and endpoint overrides are read from environment variables and can also be overridden at runtime with `--base_url`, `--api_key`, and `--timeout`.

The recommended public pattern is:

```yaml
qwen3vl32b_thinking:
  api_type: 3rd_openai
  model: Qwen3-VL-32B-Thinking
  base_url_env: OPENAI_BASE_URL
  api_key_env: OPENAI_API_KEY
  temperature: 0.6
  repetition_penalty: 1.05
  max_tokens: 16384
  timeout: 600
```

Example environment variables:

```bash
export OPENAI_BASE_URL="https://your-openai-compatible-endpoint/v1"
export OPENAI_API_KEY="your_api_key"
```

See `configs/models.example.yaml` and `.env.example` for ready-to-copy public examples.

## Evaluate CUARewardBench

### Full Benchmark Evaluation

```bash
python3 -m cuarewardbench.cli.eval_benchmark \
  --annotation_file data/annotations/cuarewardbench-v0.4.json \
  --trajectory_root data/trajectories/osworld_verified \
  --prompt_dir configs/prompts \
  --eval_mode sewsm_thinking \
  --model_config qwen3vl32b_thinking_tione_config \
  --num_workers 8 \
  --max_screenshots 20 \
  --output_dir outputs/crm_results
```

Important arguments:

| Argument | Description |
|---|---|
| `--annotation_file` | Path to `cuarewardbench-v0.4.json` or JSONL annotation file. |
| `--trajectory_root` | Root directory containing trajectories. |
| `--prompt_dir` | Directory containing `osworld_<eval_mode>.json` prompt files. |
| `--eval_mode` | Reward prompt/evaluation mode. |
| `--model_config` | Model config key in the current registry. |
| `--max_screenshots` | Max screenshots per trajectory; `20` is the historical default. |
| `--output_dir` | Directory for detailed results and metrics. |

### Recompute Metrics Only

If `detailed_results_*.json` already exists in the output directory, metrics can be recomputed without calling the model:

```bash
python3 -m cuarewardbench.cli.eval_benchmark \
  --only_metric \
  --annotation_file data/annotations/cuarewardbench-v0.4.json \
  --trajectory_root data/trajectories/osworld_verified \
  --prompt_dir configs/prompts \
  --eval_mode sewsm_thinking \
  --model_config qwen3vl32b_thinking_tione_config \
  --max_screenshots 20 \
  --output_dir outputs/crm_results
```

### Resume Behavior

The evaluator writes `detailed_results_*.json` incrementally. When restarted with the same output directory and filename configuration, it loads existing valid results and skips already evaluated `(model_setting, task_id)` pairs.

Notes:

- Completed and saved tasks are skipped.
- Tasks that were in-flight when the process stopped are rerun.
- Entries with empty or failed LLM output are cleaned and reevaluated.

## Evaluation Modes

| Mode | Reward type | Description |
|---|---:|---|
| `zerogui` | ORM | Trajectory-level success evaluation using ZeroGUI-style prompt. |
| `sewsm_thinking` | ORM + PRM | Screenshot-based trajectory analysis and step reward parsing for the maintained public prompt set. |
| `opencua_reflect_thinking` | PRM | Thinking-model reflection prompt for step-level process reward evaluation. |

Prompt files are stored in:

```text
configs/prompts/osworld_<eval_mode>.json
```

## Outputs

A benchmark run writes files like:

```text
outputs/<run_name>/
├── detailed_results_evalmode_<mode>_cuarewardbench-v0.4_<model>.json
├── metrics_evalmode_<mode>_cuarewardbench-v0.4_<model>.json
└── metrics_evalmode_<mode>_cuarewardbench-v0.4_<model>.xlsx  # if openpyxl is installed
```

The metrics JSON contains:

- `trajectory_reward_metrics`
  - `overall`
  - `by_task_type`
  - `by_model_setting`
  - `by_step_num`
- `action_reward_metrics`
  - `overall`
  - `by_task_type`
  - `by_reward_type`

Core metrics include:

- Precision
- NPV
- Recall
- Specificity
- Overall Accuracy
- F1
- TP / FP / FN / TN

## Historical Qwen3-VL-32B Reference Run

The main regression target for the packaged benchmark path is the latest historical Qwen3-VL-32B-Thinking run:

```text
../metrics_evalmode_sewsm_thinking_cuarewardbench-v0.4_Qwen3-VL-32B-Thinking.json
```

The inferred configuration is:

```text
model_config:     qwen3vl32b_thinking_tione_config
eval_mode:        sewsm_thinking
prompt:           configs/prompts/osworld_sewsm_thinking.json
max_screenshots:  20
exp_suffix:       empty
```

Run:

```bash
bash scripts/reproduce_qwen3vl32b_final.sh
```

This writes to:

```text
outputs/reproduce_qwen3vl32b_final/
```

As with any live model rerun, detailed outputs can still differ slightly because remote model services and reasoning traces are not perfectly deterministic. Use `--only_metric` when you want parser/metrics regression coverage without making new API calls.

## Evaluate New Agent Trajectories

CUARewardBench also includes a utility for evaluating newly generated UI-agent rollouts.

### Single Trial

```bash
python3 -m cuarewardbench.cli.eval_trajectory \
  --traj_dir /path/to/trial_1 \
  --prompt_dir configs/prompts \
  --eval_mode sewsm_thinking \
  --model_config qwen3vl32b_thinking_tione_config \
  --num_workers 8 \
  --max_screenshots 34
```

Expected trajectory layout:

```text
/path/to/trial_1/
└── {task_type}/
    └── {task_id}/
        ├── traj.jsonl
        ├── result.txt
        ├── step_reset_*.png
        ├── step_1_*.png
        └── ...
```

### Multi-Trial Merged Evaluation

Use the unified script for both single-trial and multi-trial evaluation:

```bash
BASE_DIR=/path/to/runs \
TRIAL_PREFIX=trial \
TRIAL_RANGE=1-3,5 \
OPENAI_BASE_URL=https://your-openai-compatible-endpoint/v1 \
OPENAI_API_KEY=your_api_key \
bash scripts/run_eval_trajectories.sh
```

Alternatively, pass explicit directories:

```bash
TRAJ_DIRS=/path/to/trial_1,/path/to/trial_2 bash scripts/run_eval_trajectories.sh
```

This merges multiple trial directories into one thread pool to avoid low parallelism near the end of each trial. The script is fully environment-variable configurable and does not contain any embedded credentials or service-specific defaults.

Notes:

- `result.txt` and `PENDING_FOR_RM` conventions come from the upstream trajectory-running pipeline.
- Trajectory evaluation outputs are currently written next to each trajectory, matching the historical workflow.

## Voting and UPE

### Explicit Input Files

```bash
python3 -m cuarewardbench.cli.vote \
  --vote_mode upe \
  --reward_type or \
  --input_files outputs/model_a/detailed_results.json outputs/model_b/detailed_results.json \
  --output_dir outputs/upe_orm
```

### Registry-Based Config

```bash
python3 -m cuarewardbench.cli.vote \
  --vote_mode upe \
  --vote_config upe_orm_2_qwen3 \
  --reward_type or \
  --output_dir outputs/upe_orm
```

Voting modes:

| Mode | Description |
|---|---|
| `upe` | Output only when all RMs unanimously agree; otherwise `None`. |
| `majority` | Positive if more than half of RMs vote positive. |
| `majority_dual` | Positive/negative only when one side has majority; tie gives `None`. |
| `all` | Positive only when all RMs vote positive; otherwise negative. |
| `one` | Positive when any RM votes positive. |

Future improvements:

- Move voting file lists from the built-in registry to YAML.
- Add more end-to-end ORM and PRM UPE reproduction examples.

## Development Notes

Repository maintenance notes:

- Use `data_engine/eval_traj` as the behavior reference if logic needs to be backported or verified.
- Treat `results/cuarewardbench` as an older implementation that may be stale.
- Public entrypoints use `python3 -m cuarewardbench.cli.*` or `bash scripts/*.sh`.
- Existing detailed results can be regression-checked with `--only_metric` when you want deterministic parser/metrics validation without new model calls.

## Citation

If you use CUARewardBench, please cite the arXiv paper:

```bibtex
@misc{lin2025cuarewardbench,
  title         = {CUARewardBench: A Benchmark for Evaluating Reward Models on Computer-using Agent},
  author        = {Haojia Lin and Xiaoyu Tan and Yulei Qin and Zihan Xu and Yuchen Shi and Zongyi Li and Gang Li and Shaofei Cai and Siqi Cai and Chaoyou Fu and Ke Li and Xing Sun},
  year          = {2025},
  eprint        = {2510.18596},
  archivePrefix = {arXiv},
  primaryClass  = {cs.SE},
  doi           = {10.48550/arXiv.2510.18596},
  url           = {https://arxiv.org/abs/2510.18596}
}
```

A machine-readable citation file is available at `CITATION.cff`.

## License

- Repository-authored code, annotations, metadata, and documentation are released under the Apache License 2.0. See `LICENSE`.
- Trajectory screenshots/images are not redistributed in this repository; users download the original upstream archives and preprocess them locally.
- `traj_tran.jsonl` is kept as part of the current normalized manifest where present; no additional data-format change is planned for this item.

## Acknowledgements

CUARewardBench builds on OSWorld-style desktop-agent tasks and upstream trajectory archives from `xlangai/ubuntu_osworld_verified_trajs`. Please follow the upstream dataset terms when downloading and preprocessing trajectory screenshots/images.
