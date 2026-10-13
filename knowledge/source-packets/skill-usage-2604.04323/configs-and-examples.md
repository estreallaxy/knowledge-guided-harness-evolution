# Configs and examples

# Official Experiment Configuration

|Settings|Configure Directory|Major variances|
| --- | --- | --- |
| SkillsBench | `official-code/experiments/configs/skillsbench/` |Claude, Kimi, Qwen three sets of operating configurations.|
| Terminal-Bench 2.0 | `official-code/experiments/configs/terminalbench/` |Claude, Kimi, Qwen three sets of operating configurations.|

The configuration can only be explained with the corresponding paper version, code review, task data and the model environment. The results of a run in a paper cannot be reproduced independently by a single YaML.

# The official process entrance

The official repository divided the process into four steps:

1.`scripts/prepare_experiment.py`: Download or organise experimental materials, generate task catalogues and Harbor configurations.
2.`scripts/retrieve_skills.py`: Job search candidate skills.
3.`scripts/query_specific_refinement.py`: Explore, diagnose and generate mission conditions skills in the mission environment.
4. `scripts/check_skill_usage.py`with`scripts/calculate_results.py`: Check the use of skills in trajectories and summarize results.

Query-special access:

```bash
python scripts/query_specific_refinement.py prepare \
  --tasks-dir <tasks-with-retrieved-skills> \
  --workspace <isolated-workspace> \
  --agent <agent> \
  --model <model>

harbor run -c <generated-config>

python scripts/query_specific_refinement.py collect \
  --tasks-dir <tasks-with-retrieved-skills> \
  --workspace <isolated-workspace>
```

Additional data and external reliance on the papers must be obtained before running. ReADME ReadME points to Hugging Face dataset`Shiyu-Lab/Skill-Usage`; large data is not included in the source package.

# Local Save Range

`official-code/`saves core scripts, search services, six sets of experimental configurations, task query metadata, three types of search, Skill-creator for paper methods. Job Full Set, Terminal-Bench 2.0 Copy, Run Cache and Download data are not in this directory.
