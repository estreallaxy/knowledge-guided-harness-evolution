# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `requirements.txt`
- `src/tools/config.py`
- `scripts/run_program_critic.sh`
- `scripts/run_program_infer.sh`
- `scripts/run_qa_critic.sh`
- `scripts/run_qa_infer.sh`
- `scripts/run_toxicity_critic.sh`
- `scripts/run_toxicity_infer.sh`

## Upstream command excerpts

```text
conda create --name critic python=3.8
conda activate critic
pip install -r requirements.txt
```

```text
@inproceedings{
    gou2024critic,
    title={{CRITIC}: Large Language Models Can Self-Correct with Tool-Interactive Critiquing},
    author={Zhibin Gou and Zhihong Shao and Yeyun Gong and yelong shen and Yujiu Yang and Nan Duan and Weizhu Chen},
    booktitle={The Twelfth International Conference on Learning Representations},
    year={2024},
    url={https://openreview.net/forum?id=Sx038qxjek}
}
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
