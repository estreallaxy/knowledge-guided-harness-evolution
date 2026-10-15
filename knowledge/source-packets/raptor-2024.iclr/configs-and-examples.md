# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `requirements.txt`

## Upstream command excerpts

```text
git clone https://github.com/parthsarthi03/raptor.git
cd raptor
pip install -r requirements.txt
```

```text
import os
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"

from raptor import RetrievalAugmentation

# Initialize with default configuration. For advanced configurations, check the documentation. [WIP]
RA = RetrievalAugmentation()
```

```text
with open('sample.txt', 'r') as file:
    text = file.read()
RA.add_documents(text)
```

```text
question = "How did Cinderella reach her happy ending?"
answer = RA.answer_question(question=question)
print("Answer: ", answer)
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
