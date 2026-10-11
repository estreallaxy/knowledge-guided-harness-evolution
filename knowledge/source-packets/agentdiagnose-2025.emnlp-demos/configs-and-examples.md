# Configs and examples

## 官方配置

AgentDiagnose 没有 YAML/TOML 形式的实验配置。可配置项分布在三处：CLI 参数、环境变量、前端构建配置。

| 配置类别 | 位置 | 内容 |
| --- | --- | --- |
| 评分器 → 模型映射 | `official-code/evaluate_trajectories.py:84-88` | `reasoning_quality` → `gemini-2.5-pro-exp-03-25`，`objective_quality` → `gemini-2.0-flash`，`navigation_path` → `no_model_needed`（不走 LLM）。该字典在批量入口内硬编码，覆盖各 scorer 类自身的 `model` 默认值。 |
| 评分器类默认模型 | `official-code/evaluator/scorers/reasoning_quality.py:37`、`objective_quality.py:32` | 分别为 `gemini-1.5-pro` 与 `gemini-2.5-pro-exp-03-25`。直接实例化 scorer 时用的是这一组。 |
| LLM 凭据 | `official-code/evaluator/scorers/reasoning_quality.py:151`、`objective_quality.py:98` | 环境变量 `LLM_API_KEY`；两处均先 `load_dotenv()`，即支持项目根放 `.env`。 |
| Dashboard 数据通道 | `official-code/dashboard/backend/main.py:1399` | 环境变量 `DASHBOARD_DATA_FILE` 指向 pickle；由 `web_dashboard.py` 代填，一般无需手设。 |
| 隧道令牌 | `official-code/dashboard/web_dashboard.py:32` | 环境变量 `CLOUDFLARE_TUNNEL_TOKEN`，仅在 `--enable-tunnel` 下使用。 |
| 前端依赖与脚本 | `official-code/dashboard/package.json` | SvelteKit 2 + Svelte 4 + Vite 5 + Tailwind 3；`plotly.js-dist` 为运行时依赖。 |
| 前端端口约定 | `official-code/dashboard/vite.config.ts:6-7`、`dashboard/web_dashboard.py:344` | 开发态 `/api` 代理到 `localhost:9080`；后端端口 = 前端端口 + 1000。 |
| 静态部署 | `official-code/dashboard/svelte.config.js` | `@sveltejs/adapter-static`，产物目录 `build/`，`BASE_PATH` 可控。 |

仓库没有任何 Python 依赖清单（无 `requirements.txt` / `pyproject.toml` / `setup.py` / `environment.yml`）。按源码 import 反推的依赖为：`litellm`、`openai`、`pydantic`、`python-dotenv`、`tiktoken`、`pandas`、`tqdm`、`spacy` + `benepar`（需 `en_core_web_md` 与 `benepar_en3` 模型）、`sentence_transformers`、`faiss`、`numpy`、`scikit-learn`、`plotly`、`flask`、`fastapi` + `uvicorn`。这些版本组合未被固定，是接入时的主要不确定项。

## 官方流程入口

`launch_dashboard.sh` 把全部步骤串成一条链路：

| 步骤 | 命令 | 产物 |
| --- | --- | --- |
| 1. 动词-名词标注 | `python generate_verb_nouns.py --input-dir <trajs> --output-dir <labeled>` | 带 root verb/noun 与 pairs 的轨迹 JSON |
| 2. 推理词云 | `python generate_tag_cloud.py --input-dir <labeled> --output-dir tag_cloud --tag-source reasoning --all-ngrams` | 1/2/3/4-gram 词云 JSON |
| 3. 动作短语词云 | `python generate_tag_cloud.py --input-dir <labeled> --output-dir tag_cloud --tag-source action_phrases --all-ngrams` | verbs/nouns/pairs 词云 JSON |
| 4. 嵌入 | `python generate_embeddings.py --input-dir <labeled> --output-dir embeddings_output` | `Qwen3-Embedding-0.6B` 向量 + FAISS 索引 |
| 5. 评估 + 起服务 | `python evaluate_trajectories.py --input <trajs> --scorers reasoning_quality objective_quality --output-json examples/results.json --web-dashboard --dashboard-host 0.0.0.0 --dashboard-port 8080 --no-auto-browser` | 分数 JSON + dashboard |

单条轨迹目录的最小调用（源自仓库 README）：

```bash
export LLM_API_KEY="your-api-key-here"

python evaluate_trajectories.py \
  --input examples/sample_trajectories \
  --scorers reasoning_quality objective_quality \
  --output-json results.json

# 只估算 token 与成本，不发 API 请求
python evaluate_trajectories.py \
  --input examples/sample_trajectories \
  --scorers reasoning_quality objective_quality \
  --dry-run
```

论文 Listing 1（PDF p.5）给的是三个评分器同时开启的形式：

```bash
python evaluate_trajectories.py \
  --input ./input.json \
  --scorers reasoning_quality objective_quality navigation_path \
  --output-json output.json
```

`navigation_path` 不调用 LLM，但其 `score` 恒为 `0.0`（见 `navigation_path_scorer.py:43`），开启它只增加 `details` 里的导航统计，不改变加权总分。计分维度实际来自 `reasoning_quality`（含四个子维度）与 `objective_quality`。

数据入口：`--input` 指向一个目录，`load_trajectories` 用 `glob("*.json")` 收集文件并以文件名去掉 `trajectory_` 前缀作为轨迹 id（`evaluate_trajectories.py:36-47`）。轨迹 JSON 的形状由 `Trajectory.from_json` 定义（`evaluator/trajectory.py:179-206`）。

接入自有 harness 时的扩展点：为 `Trajectory` 增加一个 `from_<format>` 类方法（参照 `:80-169` browsergym、`:208-338` CUGA、`:340-460` Synatra、`:462-637` AgentTrek 四个现成实现）。

## 本地保存范围

`official-code/` 保存 32 个文件、约 328KB：轨迹解析与五个评分维度、CLI 与 dashboard 前后端入口、嵌入与词云生成、SvelteKit 页面源码与其构建配置。

未纳入本来源包的内容：

| 未纳入项 | 原因 |
| --- | --- |
| `examples/sample_trajectories/`（9 个 JSON，合计 12MB） | **示例轨迹未纳入**。最大的 `trajectory_0003.json` 为 2.9MB，最小的 `trajectory_0004.json` 也有 191KB，无 <100KB 的文件可作格式样例。轨迹 JSON 的字段结构改由 `evaluator/trajectory.py:30-70`、`:171-206` 的 `Action`/`Trajectory` 定义说明。 |
| 根 `.gitignore`、`dashboard/.gitignore` | 仓库卫生文件，与机制无关。 |
| `dashboard/.github/workflows/deploy.yml` | GitHub Pages 部署 CI，本地接入不需要。 |
| 运行产物（`tag_cloud/`、`embeddings_output/`、`results.json`、`*_labeled/`） | 需运行后生成，且体积随数据增长。 |

另有两项属于上游快照自身的缺口，不是本来源包的取舍：

| 上游缺口 | 影响 |
| --- | --- |
| `dashboard/src/lib/components/` 不存在 | `+page.svelte:4-10` import 了 7 个组件（`PlotComponent`、`TrajectoryView`、`MetricsGrid`、`EmbeddingVisualization`、`NavigationPathView`、`ReasoningTagCloud`、`ActionPhrasesTagCloud`），但这些文件不在 `6ac7bedd` 提交中，前端无法直接 `npm run build`。 |
| `static/favicon.png` 不存在 | `app.html:5` 引用了它，仅影响图标。 |

因此本来源包可验证的是评估后端与数据管线；dashboard 的完整渲染需要先补齐缺失的前端组件。
