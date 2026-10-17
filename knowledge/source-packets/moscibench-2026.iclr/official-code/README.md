<div align="center">

<img src="assets/logo.png" alt="MoSciBench Logo" width="180" style="border-radius: 15px;">

# MoSciBench: Multimodal Scientific Discovery Benchmark

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Benchmark](https://img.shields.io/badge/Benchmark-Multimodal_Science-0A7B83?style=flat-square)](#data-information)
[![Framework](https://img.shields.io/badge/Framework-Agentic_Evaluation-1E88E5?style=flat-square)](#repository-layout-brief)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

<p align="center">
  <a href="#quick-start-baseline"><img src="https://img.shields.io/badge/Quick_Start-Run_Now-green?style=for-the-badge" alt="Quick Start"></a>
  &nbsp;&nbsp;
  <a href="#download-datasets"><img src="https://img.shields.io/badge/Download-Datasets-blue?style=for-the-badge" alt="Download Datasets"></a>
  &nbsp;&nbsp;
  <a href="#repository-layout-brief"><img src="https://img.shields.io/badge/Project-Structure-orange?style=for-the-badge" alt="Project Structure"></a>
  &nbsp;&nbsp;
  <a href="#data-information"><img src="https://img.shields.io/badge/Data-Overview-red?style=for-the-badge" alt="Data Overview"></a>
  &nbsp;&nbsp;
  <a href="https://github.com/usail-hkust/MoSciBench/stargazers"><img src="https://img.shields.io/github/stars/usail-hkust/MoSciBench?style=for-the-badge" alt="Stars"></a>
  &nbsp;&nbsp;
  <img src="https://komarev.com/ghpvc/?username=usail-hkust&repo=MoSciBench&style=for-the-badge" alt="Profile views">
</p>

A practical benchmark framework for multimodal scientific discovery.

</div>

## News
- **2026-03-01**: Official benchmark release of **MoSciBench**. We welcome issues and will maintain an open leaderboard to continuously improve LLM agents for multimodal scientific discovery.  
  **官方发布 MoSciBench 基准**。欢迎大家提交 issues；我们会维护一个开源榜单，致力于持续提升 LLM agents 在多模态科学发现中的能力。

## TL;DR
MoSciBench is the first benchmark focused on end-to-end multimodal scientific discovery with LLM agents. Built from peer-reviewed studies via a four-stage pipeline, it spans 6 scientific domains, 7 data modalities, 5 discovery question types, and 88 tasks. Each task requires cross-modal hypothesis verification across heterogeneous data.

## Problem Setting
Given a scientific hypothesis and its associated multimodal dataset, the agent must generate executable analysis code, run it on raw data, interpret the resulting numerical outputs, and determine whether the hypothesis is supported or refuted.

## Requirements
- Python 3.9+ (recommended 3.10/3.11)
- Access to an LLM service (configure in `config/config2.yaml`)

## Install
```bash
pip install -r MoSciBench/requirements.txt
```
Optional extras for file previews:
- `openpyxl` for Excel, `pyarrow` for Parquet

## Configure Models
```bash
cp MoSciBench/config/config2.example.yaml MoSciBench/config/config2.yaml
# Edit MoSciBench/config/config2.yaml and fill in api_key/base_url/model entries
```
Tip: You can point to a custom config via env var `MOSCI_CONFIG` (if supported in your deployment).

## Download Datasets
- List datasets:
```bash
python MoSciBench/scripts/utils/download_data.py --list
```
- Download and extract (example):
```bash
python MoSciBench/scripts/utils/download_data.py health_spa
```
- Useful flags: `--status`, `--no-extract`, `--keep-zip`, `--force`



## Dataset Access

The datasets are also available for direct download at [Google Drive](https://drive.google.com/drive/folders/1dQ6gShqq-cMVuaEd1nRufn1VVBWU7w_j).
## Quick Start (Baseline)
- Single run:
```bash
python MoSciBench/run.py --dataset health_spa --baseline_name ReAct
```
- Multiple runs (for statistics):
```bash
python MoSciBench/run.py --dataset health_spa --baseline_name ReAct --num_runs 3
```

Common flags (selection):
- `--dataset`: dataset name (hyphens normalized to underscores)
- `--baseline_name`: one of `ReAct`, `DataVoyager`, `Reflexion`, `NoDataGuess`
- `--optimized_path`: output root (default `workspace`)
- `--initial_round_path`: workflows source (default `agents`)
- `--exec_model_name`: model key defined in `config2.yaml`
- `--include_workflow` / `--include_domain_knowledge`: include extra context in Analysis prompt
- `--analysis_timeout`: execution timeout in seconds (default 1800)
- `--max_retries`: max code refine retries (default 3)

## Outputs
- Logs: `logs/`
- Trajectory: `trajectory/<dataset>/baseline_<baseline>_<timestamp>.jsonl`
- Results: `workspace/<baseline>/<dataset>/workflows/round_*` (configs, CSVs, operator artifacts)

## Repository Layout (brief)
- `agents/`: baselines and workflow templates (Analysis / CodeGenerate / CodeExecute / CodeRefine)
- `benchmarks/`: evaluation base classes and helpers
- `config/`: model configs (`config2.yaml`)
- `data/`: dataset root (download/unzip here)
- `scripts/`: runtime core (async LLM, logs, trajectory, workspace setup, downloader)
- `workspace/`, `logs/`, `trajectory/`: generated during runs

## Data Information

| Name         | Domain                 | Modalities                                  | Task Num | Descriptive | Correlational | Causal Inference | Predictive | Pattern Discovery |
|:-------------|:-----------------------|:--------------------------------------------|---------:|------------:|--------------:|-----------------:|-----------:|------------------:|
| nurse_stress | health psychology      | timeseries (multi sensors), tabular         |       15 |           6 |             4 |                1 |          3 |                 1 |
| health_spa   | biomedical engineering | timeseries (multi sensors)                  |       17 |           4 |             2 |                3 |          6 |                 2 |
| terra        | earth system science   | image, tabular, timeseries                  |       14 |           4 |             3 |                2 |          2 |                 3 |
| massspecgym  | cheminformatics        | mass spectra, molecular structures, tabular |       15 |           3 |             3 |                3 |          3 |                 3 |
| pop_genetics | population genomics    | genotype matrix, tabular                    |       13 |           4 |             3 |                0 |          2 |                 4 |


## License
See `MoSciBench/LICENSE`.

---

## ⭐ Star History

<div align="center">

[![Stargazers repo roster for @usail-hkust/MoSciBench](https://reporoster.com/stars/usail-hkust/MoSciBench)](https://github.com/usail-hkust/MoSciBench/stargazers)

[![Forkers repo roster for @usail-hkust/MoSciBench](https://reporoster.com/forks/usail-hkust/MoSciBench)](https://github.com/usail-hkust/MoSciBench/network/members)

[![Star History Chart](https://api.star-history.com/svg?repos=usail-hkust/MoSciBench&type=Date)](https://star-history.com/#usail-hkust/MoSciBench&Date)

</div>

---

## Citation

```bibtex
@inproceedings{liutowards,
  title={Towards Multimodal Data-Driven Scientific Discovery Powered by LLM Agents},
  author={Liu, Fan and Zeng, Xiaozhao and Liu, Hao},
  booktitle={The Fourteenth International Conference on Learning Representations}
}
```
