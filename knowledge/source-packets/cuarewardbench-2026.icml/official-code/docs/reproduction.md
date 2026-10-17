# Reproduction Guide

This guide describes the current reproducibility workflow for CUARewardBench.

## 1. Install

```bash
python3 -m pip install -r requirements.txt
python3 -m pip install -e .
```

Optional packages:

```bash
python3 -m pip install openpyxl pillow anthropic openai
```

## 2. Prepare Data

Trajectory screenshots/images are not redistributed in this repository. Download the original upstream archives, normalize them locally, and verify trajectories:

```bash
bash scripts/download_data.sh
python3 scripts/verify_data.py --trajectory_root ../data_build_workspace/prepared/osworld_verified
```

By default, the download pipeline keeps raw/prepared cache files in the sibling workspace `../data_build_workspace/` and materializes the verified benchmark tree into the real repository directory `data/trajectories/osworld_verified/`.

## 3. Configure Model Endpoint

```bash
export OPENAI_BASE_URL="https://your-openai-compatible-endpoint/v1"
export OPENAI_API_KEY="your_api_key"
```

## 4. Run Benchmark Evaluation

```bash
python3 -m cuarewardbench.cli.eval_benchmark \
  --annotation_file data/annotations/cuarewardbench-v0.4.json \
  --trajectory_root data/trajectories/osworld_verified \
  --prompt_dir configs/prompts \
  --eval_mode sewsm_thinking \
  --model_config qwen3vl32b_thinking_tione_config \
  --base_url "$OPENAI_BASE_URL" \
  --api_key "$OPENAI_API_KEY" \
  --num_workers 8 \
  --max_screenshots 20 \
  --output_dir outputs/crm_results
```

## 5. Historical Regression Script

The reference benchmark launcher is:

```bash
bash scripts/reproduce_qwen3vl32b_final.sh
```

It is used to compare the packaged benchmark path against the historical Qwen3-VL-32B-Thinking metrics file:

```text
metrics_evalmode_sewsm_thinking_cuarewardbench-v0.4_Qwen3-VL-32B-Thinking.json
```

The script is public-safe: endpoint and credential values come only from `OPENAI_BASE_URL`, `OPENAI_API_KEY`, or explicit CLI overrides.

## 6. Metrics-Only Recompute

If detailed model outputs already exist:

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

## 7. Expected Outputs

```text
outputs/<run_name>/
├── detailed_results_evalmode_<mode>_cuarewardbench-v0.4_<model>.json
├── metrics_evalmode_<mode>_cuarewardbench-v0.4_<model>.json
└── metrics_evalmode_<mode>_cuarewardbench-v0.4_<model>.xlsx  # optional
```

## Notes on Stochasticity

Full model reruns may not exactly reproduce historical detailed outputs because model services, sampling, and reasoning traces can be non-deterministic. The parser and metrics code can still be regression-tested via `--only_metric` using fixed detailed results.
