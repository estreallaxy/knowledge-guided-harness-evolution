# Repository Guidelines

## Project Structure & Module Organization

ANCHOR is an installable Python research package organized by pipeline stage. `task_construction/` builds tasks, `trajectory_generation/` runs target agents, `auditor_agent/` performs multi-turn audits, and `evaluation_judges/` scores trajectories. Supporting modules live in `toolbox_expansion/`, `mcp_tools/`, `auditor_model_training/`, `ablation/`, `baselines/`, and `pipeline_statistics/`. `sample_data/second_phase_instructions/` is the shared interface between task creation and downstream experiments; paper assets are in `figures/`. Package metadata and dependency groups are defined in `pyproject.toml`.

## Build, Test, and Development Commands

Use Python 3.10+. Install the core package for development with `python -m pip install -e .`; add integrations with `python -m pip install -e '.[mcp,taxonomy]'` or `'.[training]'`. Build a distributable wheel with:

```bash
python -m pip wheel --no-deps --wheel-dir dist .
```

Modules support both package and direct-script execution:

```bash
python -m task_construction.fetch_opinions
python -m evaluation_judges.evaluate_cli_traj
# Equivalent legacy form: python task_construction/fetch_opinions.py
```

Most scripts are configured through module-level constants near the top of the file. Edit values such as `BASE_DIR`, `START_INDEX`, and model IDs before execution; use CLI flags only when a script explicitly defines `argparse` options. For offline toolbox checks, set `TOOLBOX_MOCK=1`.

## Coding Style & Naming Conventions

Use four-space indentation, `snake_case` for functions and files, and `UPPER_SNAKE_CASE` for configuration constants. Keep runnable modules centered on `main()` with an `if __name__ == "__main__":` guard. New package-internal imports should be relative, with a fallback only when direct script execution must remain supported. No formatter or linter is configured; keep changes PEP 8-compatible.

## Testing Guidelines

Install test tools with `python -m pip install -e '.[dev]'`, then run `python -m pytest`. Tests must remain offline and use `tmp_path` and monkeypatching for files, HTTP, models, and subprocesses. CI covers Python 3.10, 3.11, and 3.13 and enforces 75% targeted coverage. Packaging changes must also compile all packages and build a wheel. Name files `test_<module>.py` and tests `test_<behavior>`.

## Commit & Pull Request Guidelines

Recent history uses concise, imperative, scope-focused subjects (for example, `ANCHOR: code release for CLI-agent safety evaluation`). Keep commits narrowly focused and explain experimental or schema changes in the body. Pull requests should describe the affected pipeline stage, configuration used, validation performed, and any output-format changes. Link related issues and include figures or sample output when results or visual assets change.

## Security & Configuration

Never commit API keys, checkpoint UUIDs, generated credentials, or machine-specific absolute paths. Supply secrets through environment variables such as `OPENROUTER_API_KEY`, and preserve sanitized placeholders in committed examples.
