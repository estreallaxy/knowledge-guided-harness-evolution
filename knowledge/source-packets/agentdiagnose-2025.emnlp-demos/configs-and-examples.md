# Configs and examples

## Official configuration

AgentDiagnose does not have experimental configuration in YAML/TOML form. Configurable items are distributed in three places: CLI parameters, environment variables, and front-end build configuration.

|Configuration category|Location|content|
| --- | --- | --- |
|Scorer → ModelMap| `official-code/evaluate_trajectories.py:84-88` |`reasoning_quality`→`gemini-2.5-pro-exp-03-25`,`objective_quality`→`gemini-2.0-flash`,`navigation_path`→`no_model_needed`(not going LLM). This dictionary is hardcoded within the batch entry, overriding each scorer class's own default value of`model`.|
|Scorer class default model| `official-code/evaluator/scorers/reasoning_quality.py:37`, `objective_quality.py:32` |They are`gemini-1.5-pro`and`gemini-2.5-pro-exp-03-25`respectively. This group is used when instantiating scorer directly.|
|LLM credentials| `official-code/evaluator/scorers/reasoning_quality.py:151`, `objective_quality.py:98` |Environment variable`LLM_API_KEY`; both places are preceded by`load_dotenv()`, which means that the project root is supported by`.env`.|
|Dashboard data channel| `official-code/dashboard/backend/main.py:1399` |The environment variable`DASHBOARD_DATA_FILE`points to pickle; it is filled in by`web_dashboard.py`, and generally no manual setting is required.|
|tunnel token| `official-code/dashboard/web_dashboard.py:32` |Environment variable`CLOUDFLARE_TUNNEL_TOKEN`, only used under`--enable-tunnel`.|
|Front-end dependencies and scripts| `official-code/dashboard/package.json` |SvelteKit 2 + Svelte 4 + Vite 5 + Tailwind 3;`plotly.js-dist`is a runtime dependency.|
|Front-end port convention| `official-code/dashboard/vite.config.ts:6-7`, `dashboard/web_dashboard.py:344` |Development state`/api`proxies to`localhost:9080`; backend port = frontend port + 1000.|
|static deployment| `official-code/dashboard/svelte.config.js` |`@sveltejs/adapter-static`, product catalog`build/`,`BASE_PATH`are controllable.|

The repository does not have any Python dependency manifest (no`requirements.txt`/`pyproject.toml`/`setup.py`/`environment.yml`). The dependencies deduced by source code import are:`litellm`,`openai`,`pydantic`,`python-dotenv`,`tiktoken`,`pandas`,`tqdm`,`spacy`+`benepar`(requires`en_core_web_md`and`benepar_en3`model),`sentence_transformers`,`faiss`,`numpy`,`scikit-learn`,`plotly`,`flask`,`fastapi`+`uvicorn`. These version combinations are not fixed and are the main uncertainty when accessing.

## Official process entrance

`launch_dashboard.sh`strings all the steps into a link:

|step|Order|product|
| --- | --- | --- |
|1. Verb-noun annotation| `python generate_verb_nouns.py --input-dir <trajs> --output-dir <labeled>` |Trajectory JSON with root verb/noun and pairs|
|2. Reasoning word cloud| `python generate_tag_cloud.py --input-dir <labeled> --output-dir tag_cloud --tag-source reasoning --all-ngrams` |1/2/3/4-gramword cloud JSON|
|3. Action phrase word cloud| `python generate_tag_cloud.py --input-dir <labeled> --output-dir tag_cloud --tag-source action_phrases --all-ngrams` |verbs/nouns/pairsword cloud JSON|
|4. Embed| `python generate_embeddings.py --input-dir <labeled> --output-dir embeddings_output` |`Qwen3-Embedding-0.6B`vector + FAISS index|
|5. Assessment + start-up service| `python evaluate_trajectories.py --input <trajs> --scorers reasoning_quality objective_quality --output-json examples/results.json --web-dashboard --dashboard-host 0.0.0.0 --dashboard-port 8080 --no-auto-browser` |Score JSON + dashboard|

Minimal call for a single track directory (from the repository README):

```bash
export LLM_API_KEY="your-api-key-here"

python evaluate_trajectories.py \
  --input examples/sample_trajectories \
  --scorers reasoning_quality objective_quality \
  --output-json results.json

# Only estimate token and cost, do not send API requests
python evaluate_trajectories.py \
  --input examples/sample_trajectories \
  --scorers reasoning_quality objective_quality \
  --dry-run
```

Paper Listing 1 (PDF p.5) gives the form of three graders being turned on at the same time:

```bash
python evaluate_trajectories.py \
  --input ./input.json \
  --scorers reasoning_quality objective_quality navigation_path \
  --output-json output.json
```

`navigation_path`does not call LLM, but its`score`is always`0.0`(see`navigation_path_scorer.py:43`). Enabling it only increases the navigation statistics in`details`and does not change the weighted total score. The scoring dimensions actually come from`reasoning_quality`(including four sub-dimensions) and`objective_quality`.

Data entry:`--input`points to a directory,`load_trajectories`uses`glob("*.json")`to collect files and removes the`trajectory_`prefix from the file name as the track id (`evaluate_trajectories.py:36-47`). The shape of the trajectory JSON is defined by`Trajectory.from_json`(`evaluator/trajectory.py:179-206`).

Extension point when connecting to your own harness: Add a`from_<format>`class method to`Trajectory`(refer to the four ready-made implementations of`:80-169`browsergym,`:208-338`CUGA,`:340-460`Synatra, and`:462-637`AgentTrek).

## Local saving range

`official-code/`saves 32 files, about 328KB: trajectory analysis and five scoring dimensions, CLI and dashboard front-end and back-end entrances, embedding and word cloud generation, SvelteKit page source code and its construction configuration.

Contents not included in this source package:

|Not included|reason|
| --- | --- |
|`examples/sample_trajectories/`(9 JSON, total 12MB)|**Example tracks not included**. The largest`trajectory_0003.json`is 2.9MB, and the smallest`trajectory_0004.json`is 191KB. There are no files <100KB that can be used as format samples. The field structure of the trajectory JSON is changed to the`Action`/`Trajectory`definition of`evaluator/trajectory.py:30-70`and`:171-206`.|
|Root`.gitignore`,`dashboard/.gitignore`|Repository hygiene documents, regardless of mechanism.|
| `dashboard/.github/workflows/deploy.yml` |GitHub Pages deploys CI, local access is not required.|
|Run products (`tag_cloud/`,`embeddings_output/`,`results.json`,`*_labeled/`)|It needs to be generated after running, and the volume grows with the data.|

There are two other gaps that belong to the upstream snapshot itself and are not trade-offs of this source package:

|upstream gap|Influence|
| --- | --- |
|`dashboard/src/lib/components/`does not exist|`+page.svelte:4-10`imported 7 components (`PlotComponent`,`TrajectoryView`,`MetricsGrid`,`EmbeddingVisualization`,`NavigationPathView`,`ReasoningTagCloud`,`ActionPhrasesTagCloud`), but these files are not in the`6ac7bedd`submission, and the front end cannot directly`npm run build`.|
|`static/favicon.png`does not exist|`app.html:5`references it, affecting only the icon.|

Therefore, what this source package can verify is to evaluate the backend and data pipeline; complete rendering of the dashboard requires completing the missing front-end components first.
