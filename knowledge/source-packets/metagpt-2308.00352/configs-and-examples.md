# Configs and examples

# Official configuration

|Settings|Configure Directory|Main elements|
| --- | --- | --- |
|Main Configuration Template| `official-code/config/config2.yaml`、`official-code/config/config2.example.yaml` |`llm.api_key="YOUR_API_KEY"`position; run-time copy as config2.yaml and fill in real key.|
|Individual LLM samples|`official-code/config/examples/`(9)| anthropic-claude-3-5-sonnet、aws-bedrock、google-gemini、groq-llama3-70b、huoshan_ark、openai-gpt-3.5-turbo、openai-gpt-4-turbo、openrouter-llama3-70b-instruct、spark_lite。 |
|Component Configuration|`official-code/metagpt/configs/`(11)|llm/browser/embedding/file_parser/mermaid/models/redis/s3/search/workspaceetc.|

The configuration can only be explained with the corresponding paper version, code review and model environment. The results of a run in a paper cannot be reproduced independently by a single YaML.

# The official process entrance

The command verified by the official README (`official-code/README.upstream.md`in this package):

```bash
# Install (Python >=3.9,<3.12; see README:64-66)
pip install --upgrade metagpt

# Generate the configuration, then add the API key
metagpt --init-config

# Run the example
metagpt "Create a 2048 game"
```

or code entry`generate_repo("Create a 2048 game")`(RAADME:107; `official-code/metagpt/software_company.py:16-78`). Run a product that falls on`./workspace`.

=`run_tests=True`Employment QaEngineer:

1. WriterTest generation`{workspace}/tests/test_*.py`;
2. Run `python tests/…` by RunCode (timeout=10 s, `official-code/metagpt/actions/run_code.py:92-118`;
3 ... if it fails, DebugError rewrites the code and retrys it (up to 3 § 3.3).

Operating premise:

- Python >=3.9,<3.12（README:64-66）。
- OpenAI compatible API key (`official-code/metagpt/configs/llm_config.py:46-58`; default`./config/config2.yaml`and `~/.metagpt/config2.yaml`).
- Quickshots do not contain`metagpt/utils`, `tools`, `ext`, etc. quoted modules (`official-code/metagpt/team.py:24`, `official-code/metagpt/software_company.py:11` cited `metagpt.utils.*`), which need to be fully installed on their own.
- HumanEval/MBPP evaluates scripts and harness, which are not in the current snapshot (`grep -ri humaneval|mbpp`Z0XZ Z0XZ`examples/benchmark`) and repeats the paper.

# Local Save Range

`official-code/` Save `metagpt/` core packages (team, rolls five roles, actions, environment pool, schema, configs), `config/` (config2.yaml position with 9 LLM example), `README.upstream.md`, `LICENSE`. Upstream utils /tools/ext, examples/benchmark, data sets and tests are not in this directory.
