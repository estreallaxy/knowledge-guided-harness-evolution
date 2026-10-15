# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `code/requirements.txt`
- `code/demo/run_DyLAN.py`

## Upstream command excerpts

```text
@misc{liu2023dynamic,
    title={Dynamic LLM-Agent Network: An LLM-agent Collaboration Framework with Agent Team Optimization},
    author={Zijun Liu and Yanzhe Zhang and Peng Li and Yang Liu and Diyi Yang},
    year={2023},
    eprint={2310.02170},
    archivePrefix={arXiv},
    primaryClass={cs.CL}
}
```

```text
python code/MATH/eval_math.py exp/MATH/CoT None
python code/MATH/eval_math.py exp/MATH/Complex None
python code/MMLU/eval_mmlu.py exp/MMLU/mmlu_optimal7_7 None
python code/MMLU/eval_mmlu.py exp/MMLU/mmlu_optimal7_3 None
python code/MMLU/eval_mmlu.py exp/MMLU/mmlu_optimal7_4 None
python code/MMLU/eval_mmlu.py exp/MMLU/mmlu_optimal7_2 None
```

```text
cd code
pip install -r requirements.txt
```

```text
QUERY = "What is the sum of 1 and 2?"
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
