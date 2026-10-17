# Model API Guide

CUARewardBench calls multimodal reward models through `cuarewardbench/core/llm_eval.py`.

## Supported API Styles

Current code paths support:

- OpenAI-compatible chat/completions-style multimodal APIs via `api_type=3rd_openai` and related modes;
- Anthropic Claude via `api_type=claude` when the optional `anthropic` package is installed.

Public examples should use environment variables rather than hardcoded credentials.

## Environment Variables

Recommended public configuration:

```bash
export OPENAI_BASE_URL="https://your-openai-compatible-endpoint/v1"
export OPENAI_API_KEY="your_api_key"
```

Then pass overrides explicitly:

```bash
python3 -m cuarewardbench.cli.eval_benchmark \
  --model_config qwen3vl32b_thinking_tione_config \
  --base_url "$OPENAI_BASE_URL" \
  --api_key "$OPENAI_API_KEY"
```

`scripts/run_eval_trajectories.sh` also reads `OPENAI_BASE_URL` and `OPENAI_API_KEY`.

## Key CLI Arguments

| Argument | Meaning |
| --- | --- |
| `--model_config` | Registry key loaded from `cuarewardbench/core/config.py`. |
| `--base_url` | Runtime endpoint override. |
| `--api_key` | Runtime API key override. |
| `--timeout` | Request timeout in seconds. |
| `--eval_mode` | Prompt / reward mode. |
| `--prompt_dir` | Directory containing prompt JSON files. |
| `--prompt_file` | Prompt file override. |
| `--img_scale` | Optional image down-scaling factor. |
| `--max_screenshots` | Max screenshots sent per trajectory. |

## Prompt Modes

| Mode | Reward type | Notes |
| --- | --- | --- |
| `zerogui` | ORM | Trajectory-level success score. |
| `sewsm_thinking` | ORM + PRM | Screenshot-based trajectory analysis used by the maintained public benchmark flow. |
| `opencua_reflect_thinking` | PRM | Thinking-model reflection variant. |

Prompt files are stored in `configs/prompts/osworld_<eval_mode>.json`.

## Output Expectations

`sewsm*` prompts expect the model to return a parseable `Correctness` field, typically inside `<res_dict>...</res_dict>` or a JSON-like block. The parser includes fallback handling for common formatting variants, but public model examples should still encourage strict output formatting.

## Public Configuration Notes

- The built-in registry in `cuarewardbench/core/model_config.py` is already public-safe and environment-variable driven.
- `configs/models.example.yaml` and `.env.example` provide copyable examples for externalized configuration.
- If you need a lightweight regression check without calling a real endpoint, prefer `--only_metric` on existing detailed results.
