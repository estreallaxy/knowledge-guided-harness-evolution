# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `requirements.txt`
- `setup.py`
- `mint/tasks/in_context_examples/README.md`
- `configs/gpt-3.5-turbo-0613/F=None/max1_p1+tool+cd/code_generation/humaneval.json`
- `configs/gpt-3.5-turbo-0613/F=None/max2_p2+tool+cd/code_generation/humaneval.json`
- `configs/gpt-3.5-turbo-0613/F=None/max3_p2+tool+cd/code_generation/humaneval.json`
- `configs/gpt-3.5-turbo-0613/F=None/max4_p2+tool+cd/code_generation/humaneval.json`
- `configs/gpt-3.5-turbo-0613/F=None/max5_p2+tool+cd/code_generation/humaneval.json`
- `configs/gpt-3.5-turbo-0613/F=gpt-4-0613/PHF=no_GT-textual/max5_p2+tool+cd/code_generation/humaneval.json`
- `configs/gpt-3.5-turbo-0613/F=None/max1_p1+tool+cd/code_generation/mbpp.json`
- `configs/gpt-3.5-turbo-0613/F=None/max1_p1+tool+cd/decision_making/alfworld.json`
- `configs/gpt-3.5-turbo-0613/F=None/max1_p1+tool+cd/reasoning/gsm8k.json`
- `configs/gpt-3.5-turbo-0613/F=None/max1_p1+tool+cd/reasoning/hotpotqa.json`
- `configs/gpt-3.5-turbo-0613/F=None/max1_p1+tool+cd/reasoning/math.json`
- `configs/gpt-3.5-turbo-0613/F=None/max1_p1+tool+cd/reasoning/mmlu.json`
- `configs/gpt-3.5-turbo-0613/F=None/max1_p1+tool+cd/reasoning/theoremqa.json`
- `configs/gpt-3.5-turbo-0613/F=None/max2_p2+tool+cd/code_generation/mbpp.json`
- `configs/gpt-3.5-turbo-0613/F=None/max2_p2+tool+cd/decision_making/alfworld.json`
- `configs/gpt-3.5-turbo-0613/F=None/max2_p2+tool+cd/reasoning/gsm8k.json`
- `configs/gpt-3.5-turbo-0613/F=None/max2_p2+tool+cd/reasoning/hotpotqa.json`
- `configs/gpt-3.5-turbo-0613/F=None/max2_p2+tool+cd/reasoning/math.json`
- `configs/gpt-3.5-turbo-0613/F=None/max2_p2+tool+cd/reasoning/mmlu.json`
- `configs/gpt-3.5-turbo-0613/F=None/max2_p2+tool+cd/reasoning/theoremqa.json`
- `configs/gpt-3.5-turbo-0613/F=None/max3_p2+tool+cd/code_generation/mbpp.json`
- `configs/gpt-3.5-turbo-0613/F=None/max3_p2+tool+cd/decision_making/alfworld.json`
- `configs/gpt-3.5-turbo-0613/F=None/max3_p2+tool+cd/reasoning/gsm8k.json`
- `configs/gpt-3.5-turbo-0613/F=None/max3_p2+tool+cd/reasoning/hotpotqa.json`
- `configs/gpt-3.5-turbo-0613/F=None/max3_p2+tool+cd/reasoning/math.json`
- `configs/gpt-3.5-turbo-0613/F=None/max3_p2+tool+cd/reasoning/mmlu.json`
- `configs/gpt-3.5-turbo-0613/F=None/max3_p2+tool+cd/reasoning/theoremqa.json`

## Upstream command excerpts

```text
git clone https://github.com/xingyaoww/mint-bench
cd mint-bench
```

```text
# Install Anaconda or Miniconda first if you don't have it already.
conda env create -f environment.yml
conda activate mint
# Install the MINT package
pip install -e .
```

```text
# Obtain OpenAI API access from https://openai.com/blog/openai-api
# This key is necessary for all models since, by default, we use GPT-4 for feedback generation
export OPENAI_API_KEY='YOUR KEY HERE';

# The following keys are optional
# Will only be used if you use Bard or Claude as the evaluated model/feedback provider
# https://www.googlecloudcommunity.com/gc/AI-ML/Google-Bard-API/m-p/538517
export BARD_API_KEY='YOUR KEY HERE';
# https://docs.anthropic.com/claude/docs/getting-access-to-claude
export ANTHROPIC_API_KEY='YOUR KEY HERE';
```

```text
# Create configuration files for your experiment.
# By default configs will be saved to configs/ and model outputs will be saved to data/outputs
python mint/configs/generate_config.py
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
