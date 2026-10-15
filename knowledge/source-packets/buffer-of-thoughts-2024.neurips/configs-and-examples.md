# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `requirements.txt`
- `run_benchmarks.py`

## Upstream command excerpts

```text
git clone https://github.com/YangLing0818/buffer-of-thought-llm
cd buffer-of-thought-llm
conda create -n BoT python==3.9 
pip install -r requirements.txt
```

```text
from bot_pipeline import BoT
import argparse

parser = argparse.ArgumentParser(description='Use of argparse')

parser.add_argument('--llm_model',type=str,default='gpt-4o-mini',help='Model id of LLMs')
parser.add_argument('--embedding_model',type=str,default='text-embedding-3-large',help='Model id of embedding model')
parser.add_argument('--api_key',type=str,help='The api key of user')
parser.add_argument('--base_url',type=str,default='https://api.openai.com/v1/',help='we also support Open AI-like chat/embeddings APIs')
parser.add_argument('--rag_dir',type=str,default='./math',help='The path to save the meta buffer')

args = parser.parse_args()

llm_model = args.llm_model
embedding_model = args.embedding_model
api_key = args.api_key
base_url = args.base_url
rag_dir = args.rag_dir

prompt = "Solve the problem: Raymond and Samantha are cousins. Raymond was born 6 years before Samantha. Raymond had a son at the age of 23. If Samantha is now 31, how many years ago was Raymond's son born?"

bot = BoT(
          user_input= prompt, 
          api_key = api_key,
          model_id = llm_model,
          embedding_model = embedding_model,
          base_url = base_url,
          rag_dir = rag_dir
          )

bot.bot_inference()
```

```text
python inference.py --api_key 'Input your api key here'
```

```text
python run_benchmarks.py --task_name 'gameof24' --api_key 'input your API key here if you want to use GPT-4' --model_id 'the model ID of GPT-4 or the path to your local LLM'
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
