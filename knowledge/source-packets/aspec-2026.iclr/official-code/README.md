# Automated Stateful Specialization for Adaptive Agent Systems.

Published as a conference poster at ICLR 2026. [[Paper]](https://openreview.net/pdf?id=UESTP6dR1K)

ASpec manages the full lifecycle of specialist agents: autonomously discovering agent archetypes via evolutionary search, then cultivating their expertise through experience, mirroring how human experts learn through practice and reflection.

## Overview

The framework has three main components:

- **Architect** — an LLM-based generative process that evolves the operator pool and redesigns multi-agent architectures through creation, crossover, and pruning of specialists.
- **Meta-Controller** — a neural policy that makes a binary decision per query: retain the current architecture or resample a new one. Trained via REINFORCE to balance performance, cost, and contextual fit.
- **Specialist Operators** — agents derived from base operators (CoT, Debate, ReAct, etc.) with learned identities, directives, and persistent memory accumulated through post-execution reflection.

The methodology is split into two stages:

1. **Discovery**: the Architect iteratively explores the space of specialist archetypes using evolutionary processes (creation, crossover, pruning), then selects the top-k via a performance-diversity objective.
2. **Cultivation**: selected specialists deepen their expertise on a training corpus through execution and reflection, building structured memory entries that are semantically retrieved at inference time.

## Setup

```bash
pixi install
```

To get started using OpenRouter, please add an `OPENROUTER_API_KEY` in `.env`. Then you can run:

```bash
pixi run python -m experiments.scripts.eval_aspec --dataset MATH --split train --api-type openrouter --model [model]
```

ASpec uses [LiteLLM](https://github.com/BerriAI/litellm) under the hood for compatibility with a wide range of LLM providers.

## Citation

```bibtex
@inproceedings{
    vu2026automated,
    title={Automated Stateful Specialization for Adaptive Agent Systems},
    author={Myan Vu and Harrish Ayyanar and PANG JIANG and Anwiketh Reddy and Mayank Goel},
    booktitle={The Fourteenth International Conference on Learning Representations},
    year={2026},
    url={https://openreview.net/forum?id=UESTP6dR1K}
}
```
