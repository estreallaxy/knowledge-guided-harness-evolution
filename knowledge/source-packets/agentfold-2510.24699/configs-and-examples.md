# Configs and examples

The following content is taken from`official-code/`(revision`f72f75d8c3eb842f2bbbab096a12206ff66e270f`),
**Not executed on this machine**: You need to prepare your own`AgentFold-30B-A3B`weight and multi-card vLLM service.

## Running prerequisites

|project|Require|source|
| --- | --- | --- |
|GPU/Service|vLLM multi-instance (default 8000–8005 target model, 8006`gpt-oss-120b`)| `AgentFold/serve.sh` |
|Model weight|AgentFold-30B-A3B of the paper; **The download address and weight are not provided in the repository**|`MODEL_PATH`in`serve.sh`is empty|
| Tokenizer | `AutoTokenizer.from_pretrained("qwen3-30b-a3b")` | `AgentFold/infer.py` |
|rely|See repository root`requirements.txt`|repository root|
|external tools|Search/access tools (`inference/tool_search.py`,`tool_visit.py`), may require external retrieval of service credentials|sys.path and import of`AgentFold/infer.py`|
|Evaluation data| BrowseComp, BrowseComp-ZH, WideSearch-en, GAIA |Paper §5, PDF p.7|

## Upstream example commands

```bash
# 1) Start model service (you need to fill in MODEL_PATH first)
bash AgentFold/serve.sh

# 2) Run inference (the script selects the agent through importlib, and the entry is in AgentFold/infer.py)
python AgentFold/infer.py
```

`serve.sh`Original text (excerpt):

```bash
MODEL_PATH=""
MODEL_NAME="all_moreturn_0920"
CUDA_VISIBLE_DEVICES=0 vllm serve ${MODEL_PATH} --host 0.0.0.0 --port 8000 \
  --trust-remote-code --gpu-memory-utilization 0.95 --tensor-parallel-size 1 \
  --served-model-name ${MODEL_NAME} --disable-log-requests &
# …8001–8005 isomorphic; 8006 uses gpt-oss-120b (tensor-parallel-size 2)
```

## Unconfirmed items (written as unknown)

- The exact command line parameters of`AgentFold/infer.py`: This package does not check the correspondence between the`argparse`definition and the paper settings one by one.
- The paper's experimental seed, temperature, and maximum number of rounds (the paper mentions an upper limit of 100 rounds of evaluation and 500 rounds of expansion) are the default values in the code.
- Training side: SFT data structure and hyper-participation training script are not included in this snapshot.
- The full text of the prompt word for the folding instruction: the paper has a description, and the template position in the code needs to be further positioned (prompt splicing within`infer.py`).
