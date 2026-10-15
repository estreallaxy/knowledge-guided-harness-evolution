# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `pyproject.toml`
- `tests/pat/slicers/test_slicer_main.py`
- `src/r2e/config.yml`
- `src/r2e/llms/base_runner.py`
- `src/r2e/llms/openai_runner.py`
- `src/r2e/llms/vllm_runner.py`
- `src/r2e/repo_builder/run_pycg.py`
- `src/r2e/pat/dependency_slicer/slicer_main.py`

## Upstream command excerpts

```text
2. Create a venv, clone, and install.
```

```text
## Key Concept: Equivalence Test Harnesses

R2E introduces **Equivalence Tests**, a test that checks if two pieces of code are equivalent. In the context of R2E, an **Equivalence Test** checks if the output of a function/method in a repository is the same as the output of the generated code for the same function/method. Here's an overview of the key principles of R2E:

| **Principle** | **Description** |
|---------------|-----------------|
| **Equivalence Tests** | R2E generates tests that use the ground truth implementation to check equivalence, avoiding predicting test outputs.|
| **Complete Harness** | Generates harnesses with complete setup info (e.g., files, DB connections) instead of simple I/O examples. |
| **Sliced Context** | Leverages dependency slicing to provide minimal, relevant context, for test generation. |
| **Coverage**  | Filters incorrect tests and assesses test quality using branch coverage.|

Find more details and examples at [r2e.dev](https://r2e.dev) and in our [paper](https://r2e.dev/pdfs/paper.pdf).

## Usage

R2E provides a convenient CLI to work with. The usual steps are as follows: 
(1) [setup and extract functions from repositories](#1-setup-and-extract), 
(2) [build and install repositories](#2-build-and-install), and
(3) [generate and execute **Equivalence Tests**](#3-generate-and-execute-tests)

Find the complete CLI documentation at [CLI.md](./docs/CLI.md). Below is a quickstart guide:

### 1. Setup and Extract

First, choose a unique experiment id (e.g., `quickstart`) that you can reuse for the entire workflow. Then setup repositories and 
```

```text
<details>
<summary><code>Output</code></summary>
```

```text
</details>

> [!Note]
> We also support copying from a local path, or processing a list of URLs/local paths from a json file ([cli docs](./docs/CLI.md)).
>
> During extraction all repos cloned into REPOS_DIR are processed. The extracted functions and methods are written to a JSON file. Use `--overwrite_extracted` to overwrite any existing results.

### 2. Build and Install

**Docker Mode:** By default, all repos in REPOS_DIR are installed in a Docker image for sandboxed execution. Find the generated dockerfile in REPOS_DIR. Useful reference: [install docker](http://docs.docker.com/engine/install/)

**Local Mode:** Use `--local` which will suggest the steps ***you need to take to manually*** to install repos.
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
