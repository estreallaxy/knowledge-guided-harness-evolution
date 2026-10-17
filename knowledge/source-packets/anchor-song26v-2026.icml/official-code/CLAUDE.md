# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

ANCHOR is a research pipeline (code release for an ICML publication) that evaluates CLI-agent
safety by constructing harmful tasks from real U.S. federal criminal cases, running them
through CLI agents (Claude Code, Gemini-CLI, OpenClaw), and judging the resulting trajectories
for refusal, harm, and catastrophic impact. This is offline safety-evaluation research
tooling — not a deployed service or stable public API, although its modules are packaged for
installation and reuse. Treat harmful-content-adjacent code (task
prompts, dark-trait training data, auditor strategies) as the object of study, not as content
to produce fresh instances of.

The repository uses setuptools through `pyproject.toml` and builds as the
`anchor-safety-eval` distribution. Pipeline directories are importable packages, while their
runnable modules remain independently executable. There is no configured linter or automated
test suite under `tests/` with GitHub Actions coverage and build checks.

## Running the code

Use Python 3.10+ and install the core package in editable mode with
`python -m pip install -e .`. Optional dependency groups are `mcp`, `taxonomy`, `training`,
and `dev`; for example, run `python -m pip install -e '.[mcp,taxonomy]'`. The training extra
provides common numerical and dataset dependencies, but the platform-specific `tinker` and
`tinker_cookbook` SDKs must still be provisioned in the training environment. Most auditor
scripts fall back to an OpenAI-compatible API when Tinker is unavailable. The `claude` CLI
and `node` must be on `PATH` for Claude Code harnesses.

Build and validate the distribution with:

```bash
python -m compileall -q ablation auditor_agent auditor_model_training baselines \
  evaluation_judges mcp_tools pipeline_statistics task_construction \
  toolbox_expansion trajectory_generation
python -m pip wheel --no-deps --wheel-dir dist .
```

Install development dependencies and run the offline suite with:

```bash
python -m pip install -e '.[dev]'
python -m pytest
```

Tests must not call live APIs or launch real CLI agents. Use `tmp_path`, `monkeypatch`, and
deterministic fake responses. The CI workflow in `.github/workflows/tests.yml` runs Python
3.10, 3.11, and 3.13, requires 75% coverage on the deterministic modules listed there,
compiles the package tree, and builds a wheel.

Every runnable script follows the same shape: a `CONFIGURATION` block of module-level
constants near the top (`BASE_DIR`, `JSON_FILE`, `START_INDEX`, `NUM_SAMPLES`,
`MAX_PARALLEL_WORKERS`, model IDs, etc.), then a `main()` invoked via `if __name__ ==
"__main__"`. There are no CLI argument parsers in most scripts — **edit the constants at the
top of the file**, not flags, unless a script explicitly uses `argparse`
(`evaluate_petri_trajectories.py`, `auditor_tool_setup.py` are exceptions).

Prefer module execution after installation; direct paths remain supported for compatibility:

```bash
python -m task_construction.fetch_opinions
python -m trajectory_generation.run_claude_code
python -m evaluation_judges.evaluate_cli_traj
```

### Placeholders that must be filled in before running

This is a sanitized code release — real keys, checkpoint IDs, and absolute paths are
replaced with placeholders throughout (~25 files). Before running any script, check for and
replace:
- `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY`, `TINKER_API_KEY` — read via `os.environ.get(...)`
  in most scripts; export them rather than hardcoding.
- `YOUR_SFT_CHECKPOINT_UUID` / `YOUR_RL_CHECKPOINT_UUID` — Tinker checkpoint IDs for the
  trained auditor model (`auditor_model_training/`, `ablation/`, `toolbox_expansion/`).
- `/path/to/anchor`-style `BASE_DIR` constants — output directory roots, generally
  overridable via a `BASE_DIR` env var where noted in each subdirectory's README.

## Architecture: pipeline stages and data flow

The stages run in sequence, each stage's output feeding the next. Data is passed as JSON
files, not through any shared runtime/framework:

1. **`task_construction/`** — Turns CourtListener federal-case opinions into neutral-language
   task prompts. `fetch_opinions.py` → `fetch_usc.py` → `generate_classifications.py`
   (extract scenario + bad action, filter to computer-assistable crimes) →
   `clean_task_instructions.py` → `neutral_rewriting.py` → `validate_refinements_3_judges.py`
   (3-judge validation the rewritten task still matches the original illegal behavior). Output
   feeds `sample_data/second_phase_instructions/` — the canonical task set referenced
   everywhere downstream as "ANCHOR-Seed"
   (`sample_data/second_phase_instructions/sampled_300_first_iteration_3_judges.json`).

2. **`trajectory_generation/`** — Runs the ANCHOR-Seed tasks against CLI agents directly
   (single-shot, no adversarial auditor): `run_gemini_cli_phase1.py`/`run_gemini_cli_phase2.py`
   (Gemini-CLI, configurable to open-source models via `USE_LOCAL_MODEL`/`LOCAL_MODEL_URL`/
   `LOCAL_MODEL_NAME`/`LOCAL_MODEL_API_KEY` env vars) and `run_claude_code.py` (Claude Code +
   MCP server integration).

3. **`auditor_agent/`** — The multi-turn adversarial auditor (RQ2/RQ3). Loop per case: PLAN
   (auditor generates a todo list + instruction) → EXECUTE (target CLI agent runs it) →
   EVALUATE (auditor compares output against the task, emits PASS/FAIL) → repeat on FAIL.
   One script per target harness: `auditor_claude_code.py`, `auditor_gemini_cli.py`,
   `auditor_openclaw.py`. Output structure per case:
   `{BASE_DIR}/subagent{N}/{case_id}/program0/` plus `auditor_todo.md`/`auditor_log.md`.

4. **`toolbox_expansion/`** — Wraps the `auditor_agent/` Claude-Code auditor with a Phase-0
   step (`auditor_with_toolbox.py`) that configures the **target's** workspace before turn 1,
   for scenario realism: a generic system prompt injected via `--append-system-prompt`
   (`tool_system_prompt.py`), mundane workspace files (`tool_workspace_files.py`), and
   FastMCP tool servers registered via `.mcp_config.json`/`--strict-mcp-config`
   (`tool_mcp_servers.py`). `TOOLBOX_MOCK=1` runs these offline with hardcoded content;
   `TOOLBOX_ENABLED=0` disables the toolbox entirely.

5. **`auditor_model_training/`** — SFT (`training_framework/supervised/train.py`) then RL
   (`training_framework/rl/train.py`) fine-tuning of the auditor model for dark-personality
   traits, using recipes in `training_framework/recipes/`. Training data generated by
   `sft_data/sft_data_gen.py` from `dark_trait_*.json` seed data. `dark_triad_eval.py`
   evaluates the resulting model against baseline/roleplay/fine-tuned conditions.

6. **`evaluation_judges/`** — All judges call `google/gemini-2.5-flash` via OpenRouter and
   score a trajectory against its *original* (pre-rewrite) harmful task, not the neutralized
   prompt. Four independent dimensions, each a separate script:
   `evaluate_cli_traj.py` (refusal yes/no + harm 0–100) → `trajectory_evaluation.json`;
   `evaluate_catastrophic_impact.py` (0–100, financially-stretched "finbig" rubric — see
   table in README — with anti-disclaimer guidance so the judge isn't fooled by hedging) →
   `catastrophic_evaluation_v2.json`; `evaluate_cli_behavior.py` (categorizes behavior:
   inherently harmful / facilitating harm / compliance-safety); `evaluate_extra_mile.py`
   (did the agent proactively add harm beyond what was asked). `build_taxonomy_parallel.py` →
   `build_higher_level_taxonomy.py` cluster behaviors into an action-oriented taxonomy
   afterward. These judge modules are reused as-is by `ablation/` and `baselines/petri/` to
   keep scores comparable across experiments.

7. **`ablation/`** — Isolates which auditor component matters, holding the target fixed at
   Claude Code Haiku 4.5 over the same 10 cases (indices 000–009). Each `scripts/auditor_*.py`
   removes one component from the full `auditor_baseline.py` pipeline (trained weights →
   `_vanilla_model`, strategy toolbox → `_no_toolbox`, ICRL/rewriting → `_no_icrl_norewrite`).
   Shares `response_pipeline.py`/`xml_response_formatter.py` helpers across variants. Results
   land in `./results_{condition}/`, scored with the catastrophic judge from
   `evaluation_judges/`.

8. **`baselines/petri/`** — Runs the external [Petri](https://github.com/safety-research/petri)
   conversation-only auditor (not bundled; `pip install git+https://...`) against the same
   target models, then rescoring the transcripts with ANCHOR's own judges via
   `evaluate_petri_trajectories.py --input-format {petri,easyjailbreak}` so results are
   comparable to ANCHOR's CLI-agent numbers on the same Harm & Risk Score formula.

9. **`mcp_tools/`** — LLM-simulated MCP tool responses (agents can't hit real external
   services in this sandboxed eval). Each domain (`web_browsing_tools.py`,
   `api_integration_tools.py`, `database_tools.py`, `business_tools.py`,
   `cloud_operations_tools.py`, `content_publishing_tools.py`, `personal_content_tools.py`,
   `automation_tools.py`) defines tool schemas; `server.py` intercepts calls and generates a
   realistic response via an LLM rather than executing anything real. Distinct from the
   FastMCP servers generated per-case by `toolbox_expansion/tool_mcp_servers.py`.

10. **`pipeline_statistics/`** — Read-only counters over `task_construction/` output, tracking
    survival rate through each filter stage (`count_opinions.py`, `count_courtlistener.py`,
    `count_classifications.py`, `count_clean_tasks.py`, `count_iterative_refinements.py`,
    `count_validations.py`).

Cross-cutting notes:
- `sample_data/second_phase_instructions/` is the one shared input almost every later stage
  reads from directly (hardcoded relative path `../sample_data/second_phase_instructions/...`
  in several scripts) — treat it as the interface between task construction and everything
  downstream.
- `openrouter_inference.py` at the repo root is a minimal standalone OpenRouter multi-model
  test harness, unrelated to the main pipeline — useful as a reference for the OpenRouter
  call shape used throughout, not something other stages import.
- `usc_config.json` configures which U.S. Code titles `task_construction/fetch_usc.py` pulls
  definitions for.
