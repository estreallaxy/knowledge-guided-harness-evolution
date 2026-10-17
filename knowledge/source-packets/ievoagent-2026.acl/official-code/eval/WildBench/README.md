# WildBench Evaluation

Custom scripts for evaluating IEvoAgent and baseline models on the [WildBench](https://github.com/allenai/WildBench) benchmark.

## Setup

```bash
# Clone WildBench
git clone https://github.com/allenai/WildBench.git /tmp/WildBench
cd /tmp/WildBench && pip install -e .

# Or install core dependencies
pip install -r requirements.txt
```

## Structure

- `agent_inference.py` — Adapter that wraps IEvoAgent for WildBench inference
- `test_agent.py` — Quick test to verify agent inference works
- `run_agent*.sh` — Scripts to run agent-based evaluation
- `run_vllm_*.sh` — Scripts to run vLLM-based inference
- `merge_results.py` — Merge sharded evaluation results
- `view_results.py` — View/compute scores from results
- `wildbench_data/` — WildBench v2 benchmark data

## Usage

```bash
# 1. Start vLLM server first (see AGENT_README.md)
# 2. Test agent works
python test_agent.py

# 3. Run evaluation
bash run_agent.sh
```
