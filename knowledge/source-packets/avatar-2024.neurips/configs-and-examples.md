# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `requirements.txt`
- `scripts/run_avatar_optimizer.py`
- `config/default_args.json`
- `scripts/run_avatar_flickr30k_entities.sh`
- `scripts/run_avatar_stark.sh`

## Upstream command excerpts

```text
from dspy.predict.avatar import Tool, Avatar
from langchain_community.utilities import GoogleSerperAPIWrapper, ArxivAPIWrapper

tools = [
    Tool(
        tool=GoogleSerperAPIWrapper(),
        name="WEB_SEARCH",
        desc="If you have a question, you can use this tool to search the web for the answer."
    ),
]

agent = Avatar(
    tools=tools,
    signature="question->answer",
    verbose=True,
)
```

```text
answer = agent(question)
```

```text
from dspy.teleprompt import AvatarOptimizer

def metric(example, prediction, trace=None):
    ...

teleprompter = AvatarOptimizer(
    metric=metric,
    max_iters=10,
    max_negative_inputs=10,
    max_positive_inputs=10,
)

optimized_arxiv_agent = teleprompter.compile(
    student=agent,
    trainset=trainset
)
```

```text
conda create -n avatar python=3.11
pip install stark-qa typeguard
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
