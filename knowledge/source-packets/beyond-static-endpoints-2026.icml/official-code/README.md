# ToolPro

ToolPro is a research artifact for executable tool programs in LLM agents. Instead of asking an agent to make many step-by-step API calls, ToolPro asks the model to generate a small effect-annotated program, compiles it to WebAssembly, executes it against MCP-style tools, and uses replay/fallback policies to keep writes conservative.

This repository contains both the main paper experiment scripts and the supplementary ToolPro benchmark runner.

## Start Here

| If you want to... | Read / run this |
|---|---|
| Understand the artifact quickly | [What is in this repo?](#what-is-in-this-repo) |
| Run the supplementary bench1-bench4 ToolPro path | [Supplementary benchmark quick start](#supplementary-benchmark-quick-start) |
| Run the main paper application experiments | [Main paper experiments](#main-paper-experiments) |
| See every important directory | [Repository map](#repository-map) |
| Debug setup problems | [Configuration notes](#configuration-notes) |

Chinese documentation is available in [README_zh.md](README_zh.md).

## What Is In This Repo?

ToolPro has two experiment paths:

1. **Main paper experiments** under `experiment/calculate/`
   - Application-level workflows over Memos, Directus, and MinIO.
   - Useful for the full integration picture and traffic/cost statistics.

2. **Supplementary ToolPro benchmarks** under `exp2/ToolPro/`
   - Bench1-bench4 program-mode evaluation.
   - Pipeline: model code generation -> first-layer compile gate -> Wasm execution -> validator.
   - Best entry point if you want to inspect the executable-tool-program idea directly.

At a high level, ToolPro provides:

- Code generation for tool workflows.
- Rust / Go / Lua first-layer compile checks.
- WebAssembly execution with host-side MCP-style calls.
- Effect markers for READ / WRITE operations.
- Replay-aware repair and conservative fallback modes.
- Validators for Directus / MinIO / Memos benchmark tasks.

## Repository Map

| Path | Purpose |
|---|---|
| `core/` | Execution engine, compile pipeline, Wasm runtime, replay, fallback, history |
| `client/` | Client-side code generation and route selection |
| `services/` | Query and maintenance helpers |
| `experiment/calculate/` | Main paper experiment scripts |
| `experiment/mcp-server/` | MCP-style server and tool bridge used by main experiments |
| `experiment/mcp-client/` | MCP client config and session code |
| `exp2/ToolPro/` | Supplementary ToolPro CLI and program-mode benchmark runner |
| `exp2/baseline/` | Stepwise baseline, task prompts, Directus seed/init code, validators |
| `exp2/exp_case4/` | Case 4 assets: Directus + MinIO + Memos |
| `ToolPro_Experiment/` | Example Docker Compose files for Directus, MinIO, and Memos |

## Prerequisites

- Python 3.10+
- Rust toolchain with `wasm32-unknown-unknown`
- Docker, for Directus / MinIO / Memos
- Optional: Go 1.21+ for Go and Lua first-layer paths
- An OpenRouter-compatible model endpoint for `exp2.ToolPro`

## Install

```bash
git clone https://github.com/morgen52/toolpro_icml26.git
cd toolpro_icml26

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
rustup target add wasm32-unknown-unknown
```

On Windows PowerShell, activate the environment with:

```powershell
.\venv\Scripts\Activate.ps1
```

## Environment Variables

Create a `.env` file at the repository root. Do not commit it.

For the supplementary ToolPro runner:

```text
OPENROUTER_API_KEY=...
OPENROUTER_MODEL=...
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

For the main client/server path:

```text
LLM_API_KEY=...
LLM_MODEL=...
LLM_BASE_URL=...
SERVER_URL=http://localhost:8001
```

`exp2.ToolPro` currently reads the OpenRouter-compatible variables above. If you use another provider, point `OPENROUTER_BASE_URL` at a compatible gateway or adapt `exp2/ToolPro/llm_client.py`.

## Supplementary Benchmark Quick Start

This is the most direct way to run the ToolPro program-mode artifact.

### 1. Start Required Services

Cases 1-3 require Directus. Case 4 also requires MinIO and Memos.

Example Compose files are under `ToolPro_Experiment/`:

```bash
docker compose -f ToolPro_Experiment/directus-docker/docker-compose.yml up -d
docker compose -f ToolPro_Experiment/docker-minio/docker-compose.yml up -d
docker compose -f ToolPro_Experiment/memos/docker-compose.yml up -d
```

### 2. Seed / Check Services

From the repository root:

```bash
python -m exp2.baseline init
python -m exp2.exp_case4.test.test_init_services
```

The Case 4 service check is optional if you are only running Cases 1-3.

### 3. Run ToolPro

```bash
python -m exp2.ToolPro --language rust --model env --batches 1 --cases 1,2,3,4
```

Use `--cases all` as shorthand for `1,2,3,4`. Add `-v` to print model responses, extracted source, READ/WRITE markers, compile output, and execution details.

Results are written to:

- `exp2/ToolPro/results/` for mixed runs and Cases 1-3.
- `exp2/exp_case4/results/` for some Case 4-only runs.

Each run prints `[PASS/FAIL]`; a full four-benchmark run should eventually show a pass for Cases 1-4.

## Benchmarks

| Bench | Repo case | Main challenge |
|---|---|---|
| bench1 | Case 1 | Runtime lookup of the correct pending order, then a bound write |
| bench2 | Case 2 | Loops, branching, and coordinated writes |
| bench3 | Case 3 | Non-idempotent state change plus exchange log creation |
| bench4 | Case 4 | Cross-service workflow over MinIO, Directus, Memos, and cleanup |

Prompts and validators live in `exp2/baseline/case_prompts.py`, `exp2/baseline/validator.py`, and `exp2/exp_case4/`.

## Main Paper Experiments

The main paper path lives in `experiment/calculate/`.

Before running it:

- Start the required Docker services.
- Configure `experiment/mcp-server/settings.toml`.
- Configure `experiment/mcp-client/` if your MCP client settings differ.
- Start `start_server.py` and `start_client.py` when using the full client/server stack.

Start the optional main services:

```bash
python start_server.py
python start_client.py
```

Run the full application-level script:

```bash
cd experiment/calculate
python application_test_with_dw.py
```

Run the lighter traffic-focused workflow driver:

```bash
cd experiment/calculate
python test_refactored.py --test 1 --batch 5
```

Main experiment outputs are written under `experiment/calculate/results/`.

## Common CLI Flags

| Goal | Flag |
|---|---|
| Select language | `--language rust`, `--language go`, `--language lua` |
| Use `.env` model | `--model env` |
| Run selected cases | `--cases 1,3` or `--cases all` |
| Compile only | `--skip-execute` |
| Print detailed traces | `-v` |
| Toggle replay | `--replay on` / `--replay off` |
| Change fallback policy | `--fallback-policy safe_stepwise` / `fail_fast` |
| Simulate extra RTT | `--extra-rtt-ms <milliseconds>` |
| Change client precheck | `--client-precheck strict|warn|off` |

Full CLI details are in `exp2/ToolPro/README.md` and:

```bash
python -m exp2.ToolPro --help
```

## Configuration Notes

- Keep Directus configuration consistent. `exp2/baseline/directus_tools.py` contains hard-coded Directus URL/token defaults; the initializer, runner, and validator must point to the same instance.
- Case 4 defaults are in `exp2/exp_case4/config.py`.
- `ToolPro_Experiment/` is a convenience starting point, not a required deployment layout.
- Do not use replay for nondeterministic writes unless you are intentionally running an ablation such as `--replay-allow-nondeterministic-writes`.
- If a generated program cannot be replayed safely, ToolPro is designed to fall back conservatively instead of overstating replay guarantees.

## Smoke Checks

```bash
python -m exp2.ToolPro --help
```

After installing dependencies and starting services, these checks exercise the service-facing paths:

```bash
python -m exp2.exp_case4.test.test_init_services
python test_write_mode_debug.py --help
python test_memos_rollback_mechanism.py --help
```

Most experiment checks require local services and credentials. For documentation-only changes, `git diff --check` is a useful quick sanity check.

## Background

ToolPro treats external API interaction as a representation problem. Static tool endpoints often force agents to carry control flow in their prompt state and make many stepwise calls. ToolPro instead emits an executable tool program with explicit READ/WRITE effects, executes it in a Wasm sandbox, and uses replay/fallback policies around repair.

This differs from code-as-planning work that uses code mainly as an internal scratchpad: the generated program here is the action representation over the external tool/API surface. It also differs from GraphQL or server-side batching because it does not require a predeclared schema of workflow families.
