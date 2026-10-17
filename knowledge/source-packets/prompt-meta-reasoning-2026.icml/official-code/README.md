# Prompt Optimization with Minimal Unlabeled Input via Meta-Reasoning

This is the official implementation of **MR.PEA** (Meta-Reasoning Prompt Engineering Agent), a self-supervised prompt optimization framework that operates with minimal input — a task description, one example question, and an answer format specification. MR.PEA iteratively builds task-specific knowledge through meta-reasoning, generates diverse validation examples, refines prompts, and evaluates quality. It can optionally perform web search to fill knowledge gaps.

![MR.PEA framework overview](assets/mrpea.png)

> Experiments on GSM8K and BIG-Bench Hard show MR.PEA outperforms existing baselines, achieving an average gain of **7.4%** with an optimization cost as low as **$0.01 per task**.


## Quick start

```bash
# 1. Setup environment
conda create -n mrpea python=3.10 -y && conda activate mrpea
pip install -r requirements.txt

# 2. Configure OpenAI clients
export OPENAI_API_KEY="your-key" # or set in config/mrpea_config.yaml

# 3. Set task.task_name in config/mrpea_config.yaml and run
python main.py
```

Optimization results are saved to `data/results/<task>_<timestamp>/` and logs are written to `log/`.

## Project structure

```
├── main.py                     # Entry point
├── config/
│   ├── mrpea_config.yaml       # All settings (task, model, optimization, evaluation)
│   ├── tasks_simple.yaml       # Task definitions (task description, output format and sample question)
│   └── prompts/                # Agent prompt templates
├── src/
│   ├── mrpea.py                # Core optimization orchestrator
│   ├── config_loader.py        # YAML config loading
│   ├── agents/                 # Specialized LLM agents (see Architecture below)
│   └── memory/                 # Persistent prompt/knowledge/feedback storage
├── evaluation/                 # Benchmark evaluation scripts
│   ├── eval_bbh.py             # BIG-Bench Hard
│   ├── eval_gsm8k.py           # GSM8K
│   └── dataset/                # Downloaded datasets here
├── optimized_prompts/          # Optimized prompts from MR.PEA and baselines
├── assets/                     # Images and other static assets
└── requirements.txt
```

## Configuration

All settings live in `config/mrpea_config.yaml`. API keys can be set there or via environment variables.

### Core settings

| Setting | Description |
|---|---|
| `task.task_name` | Task to optimize (must match a key in `tasks_*.yaml`) |
| `task.task_file` | Task definition file |
| `optimization.max_iterations` | Max optimization rounds (default 10) |
| `optimization.win_threshold` | Consecutive wins to early-stop (default 3) |
| `optimization.historical_prompt_limit` | Top-N historical prompts fed to refinement (default 3) |

You can also assign different models to different agents under the `agents` section. A common configuration is a **teacher-student** setup: use a stronger model for reasoning-heavy agents (`meta_reasoning`, `prompt_refinement`) and a smaller, cheaper model for `evaluation`.

### Web search mode

We use [LinkUp](https://www.linkup.so) as the web search API. To enable it, set `web_search.enabled: true` and set `max_searches` and your LinkUp API key. When enabled, the web-specific prompt templates will be loaded.

## Architecture

MR.PEA uses **6 specialized agents** (4 in no-web mode), each calling the LLM with its own system prompt:

| Agent | Role |
|---|---|
| `AbstractionAgent` | Extracts reusable strategies, principles, and evaluation criteria from examples |
| `ExampleGenerationAgent` | Generates diverse test examples for prompt evaluation |
| `PromptRefinementAgent` | Refines the current best prompt using knowledge, feedback, and history |
| `EvaluationAgent` | Compares two prompts by executing both and judging outputs |
| `WebSearchAgent` | Queries LinkUp API to fill knowledge gaps *(web mode only)* |
| `MetaDecisionAgent` | Decides if/when a web search is warranted *(web mode only)* |

**Optimization loop:** Each iteration abstracts knowledge → generates an example → refines the prompt → evaluates old vs. new → updates ranking scores. Stops early when the current best wins `win_threshold` times consecutively.

All agents share a **persistent memory** (file-based, per run) storing the prompt pool, knowledge entries, examples, feedback, and ranking scores.

## Evaluate optimized prompts

We provide optimized prompts from MR.PEA and several baseline methods (direct, CoT, OPRO, GPO, GLaPE, SPO, PromptWizard) in `optimized_prompts/`.

### 1. Download datasets

```bash
# BBH: clone into evaluation/dataset/BIG-Bench-Hard-main/
git clone https://github.com/suzgunmirac/BIG-Bench-Hard.git evaluation/dataset/BIG-Bench-Hard-main

# GSM8K: clone into evaluation/dataset/grade-school-math-master/
git clone https://github.com/openai/grade-school-math.git evaluation/dataset/grade-school-math-master
```

### 2. Run evaluation

Evaluation scripts read `openai.*` and `eval.*` from `config/mrpea_config.yaml` automatically. Just pass `--method`:

```bash
# BBH
python evaluation/eval_bbh.py --method mrpea --task movie_recommendation

# GSM8K
python evaluation/eval_gsm8k.py --method mrpea

# Override settings
python evaluation/eval_bbh.py --method mrpea --task movie_recommendation --max-questions 50
```

Logs are saved to `evaluation/log/` with per-question details (input, output, tokens, correctness, running accuracy).

<!-- ## Citation

If you use this code or the MR.PEA method in your research, please cite:

```bibtex
@inproceedings{mrpea2026,
  title     = {Prompt Optimization with Minimal Unlabeled Input via Meta-Reasoning},
  author    = {...},
  booktitle = {Proceedings of the ...},
  year      = {2026}
}
``` -->
