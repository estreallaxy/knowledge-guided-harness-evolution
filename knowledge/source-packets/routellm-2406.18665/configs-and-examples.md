# Configs and examples

The following are taken from`official-code/README.md`with`config.example.yaml`(revision
`0b64fdafe049e596a3f5657c219329f24af24198`),** not implemented on this machine**.

# Run the preconditions #

|Item|Request|Source|
| --- | --- | --- |
|Install|`pip install "routellm[serve,eval]"`or source code`pip install -e .[serve,eval]`|Upstream README Information|
|Evidence of strong/weak models|Thesis`gpt-4-1106-preview` + `Mixtral-8x7B-Instruct-v0.1`(Anyscale trustee)|Upstream README Quickstart; paper § 5.1|
| Router weights | Hugging Face `routellm/*` checkpoints, including `mf_gpt4_augmented` | `config.example.yaml` |
|Training data|Chatbot Arena Human Prejudice (`lmsys/lmsys-arena-human-preference-55k`), GPT-4 Judge Battles| `config.example.yaml` |
|Calibration data|Calibration threshold by query (Arena data for the paper)|Upstream|

# Upstream Example Command

```bash
#1) Replace with control drop-in (Python SDK)
python - <<'PY'
import os
from routellm.controller import Controller
os.environ["OPENAI_API_KEY"] = "sk-XXXXXX"
os.environ["ANYSCALE_API_KEY"] = "esecret_XXXXXX"
client = Controller(routers=["mf"], strong_model="gpt-4-1106-preview",
                    weak_model="anyscale/mistralai/Mixtral-8x7B-Instruct-v0.1")
PY

#2) Calibration threshold: to allow about 50% of requests to take a strong model
python -m routellm.calibrate_threshold --routers mf --strong-model-pct 0.5 --config config.example.yaml
# Example of upstream output: For 50.0% strong model calls for mf,

#3) Specified router for generating
#    model="router-mf-0.11593"

#4) or use OpenAI compatible services
python -m routellm.openai_server --routers mf --strong-model gpt-4-1106-preview \
  --weak-model anyscale/mistralai/Mixtral-8x7B-Instruct-v0.1
```

Configure Snippet

```yaml
#compig.example.yaml
sw_ranking:
    arena_battle_datasets:
      - lmsys/lmsys-arena-human-preference-55k
      - routellm/gpt4_judge_battles
causal_llm:
    checkpoint_path: routellm/causal_llm_gpt4_augmented
bert:
    checkpoint_path: routellm/bert_gpt4_augmented
mf:
    checkpoint_path: routellm/mf_gpt4_augmented
```

# Unrecognized entry (identified)

- The exact cross-references for each of the four routers (except for the Zoom Co. G = 10 in the paper): not checked individually.
- Thesis Table 1-4 and the corresponding command for`routellm/evals/`scripts: the evaluation code has been incorporated and the bottom third-party data set (GSM8K/MMLU/MT-Bench) is self-accessible.
- Comparison and callability of ">40% cheaper than commercial offers": The paper is in appendix E and is not reproduced in this package.
