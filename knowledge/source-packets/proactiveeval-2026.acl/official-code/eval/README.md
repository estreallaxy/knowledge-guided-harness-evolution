# This is code and results of the eval module in ProactiveEval
1. ``target_planning_result``: Contains evaluation results for all models in the target planning task. Due to submission space limitations, only 30 randomly sampled evaluation results per model are shown.
2. ``dialogue_guidance_result``: Includes evaluation results for all models in the dialogue guidance task. Similarly, only 30 randomly sampled results per model are displayed due to space constraints.
3. ``further_analysis``: Contains code and results for additional experiments, such as target density analysis, tone analysis, and the performance of the "without target" model in dialogue guidance.
4. ``Human_Evaluation``: Provides human-annotated and LLM-annotated evaluation results.
5. ``prompt``: Includes all prompts used for model generation and evaluation.

# Quickstart:
1. Create the conda environment:
```
conda create -n ProactiveEval python=3.10
conda activate ProactiveEval
pip install -r requirements.txt
```

2. Configure your API, base_url, and model in ``config.yaml``.

3. Run all evaluations using:
```
python main.py --config config.yaml
```