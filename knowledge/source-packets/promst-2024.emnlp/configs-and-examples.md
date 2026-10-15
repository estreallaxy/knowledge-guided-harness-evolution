# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `BlocksWorld/env_data_BlocksWorld/pddlgym/demo_planning.py`
- `Logistics/env_data_Logistics/pddlgym/demo_planning.py`

## Upstream command excerpts

```text
conda create -n PROMST python=3.10
conda activate PROMST
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia
conda install conda-forge::tiktoken
pip install openai --upgrade
pip install pygame
conda install conda-forge::transformers
conda install anaconda::scikit-learn
pip install gym==0.26.2
pip install pddlgym
pip install tarski
```

```text
cd /Users/Your user name/opt/anaconda3/envs/PROMST/lib/python3.10/site-packages
cp -r /Your path to PROMST/PROMST/BlocksWorld/env_data_BlocksWorld/pddlgym ./
```

```text
python env3-box-arrange-train_MCTS.py
-experiment_trial_num 1
-input_error_prompt_token_limit 15000
-model_name_promptLLM gpt-4-1106-preview
-model_name_testLLM gpt-3.5-turbo-16k-0613
-min_level 2
-n_children 8
-n_selected 2
-prompt_method PROMST
-with_score_model 'False'
-Training_path ../BoxLift/train_set/
-Testing_path ../BoxLift/test_set/
-base_path ../BoxLift/
```

```text
python env3-box-arrange-train_MCTS.py -experiment_trial_num 3 -input_error_prompt_token_limit 15000 -model_name_promptLLM gpt-4-1106-preview -model_name_testLLM gpt-3.5-turbo-16k-0613 -min_level 2 -n_children 4 -n_selected 2 -prompt_method PROMST -with_score_model 'False' -with_SumLLM 'False' -Training_path ../BoxLift/train_set/ -Testing_path ../BoxLift/test_set/ -base_path ../BoxLift/
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
