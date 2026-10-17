# AOEB

AOEB is a retrieval evaluation workspace for text, image, and multimodal
embedding models. This public version contains source code, task definitions,
and runnable entrypoints, but does not include local datasets, model weights,
logs, caches, or evaluation outputs.

## Environment

```bash
conda create -n aoeb python=3.12
conda activate aoeb
pip install torch torchvision "transformers[torch]" accelerate peft datasets
pip install "mteb==2.1.7" pytrec_eval
```

Some multimodal models require their own optional dependencies, for example
`qwen-vl-utils`, `flash-attn`, or the VISTA `visual_bge` package.

## Data And Cache Paths

Local datasets are resolved from `AOEB_DATA_ROOT` or `LOCAL_DATA_PREFIX`.
Task JSON files may use `${AOEB_DATA_ROOT}` placeholders, which are expanded
when `RetrievalTask.from_config()` loads them.

```bash
export AOEB_DATA_ROOT=/path/to/local-data
export LOCAL_DATA_PREFIX="$AOEB_DATA_ROOT"
export HF_HOME="${HF_HOME:-.cache/huggingface}"
export HF_DATASETS_CACHE="${HF_DATASETS_CACHE:-.cache/huggingface/datasets}"
export MTEB_CACHE="${MTEB_CACHE:-.cache/mteb}"
```

VISTA users can point AOEB to a local `visual_bge` source checkout if the
package is not installed:

```bash
export AOEB_VISUAL_BGE_SOURCE_DIRS=/path/to/FlagEmbedding/research/visual_bge
export AOEB_VISTA_BASE_WEIGHT_PATH=/path/to/Visualized_base_en_v1.5.pth
```

### Data Downloading

MTEB-integrated tasks specify their Hugging Face dataset references in the task
class's `metadata.dataset` field, so they can be evaluated directly with online
dataset loading. For offline evaluation, instantiate each task and explicitly
call `.load_data()` while online to preload the dataset into the local cache.
For example, in `run_batch_mteb.py`, comment out lines 763–770 to skip
`mteb.evaluate(...)` and execute only `task.load_data()` on line 761. Once the
data is cached, the task can be evaluated offline.

For AOEB tasks, download the datasets manually from Hugging Face and arrange
the files under `AOEB_DATA_ROOT` to match the paths defined in
`aoeb_ng/tasks/*.json`.

The MMRC dataset is available at
[`vec-ai/MMRC-R`](https://huggingface.co/datasets/vec-ai/MMRC-R).
The MRMR subsets are available at
[`design`](https://huggingface.co/datasets/MRMRbenchmark/design),
[`traffic`](https://huggingface.co/datasets/MRMRbenchmark/traffic),
[`negation`](https://huggingface.co/datasets/MRMRbenchmark/negation), and
[`theorem`](https://huggingface.co/datasets/MRMRbenchmark/theorem).

## Run AOEB Tasks

For common AOEB runs, edit the defaults at the top of `run_batch_aoeb.sh`.
Set `MODEL` for the model or local model path, `TASK_CONFIG_LIST` for the
AOEB task JSON files, and `OUTPUT_DIR`, `BATCH_SIZE`, `GPU_ID`, `MAX_LENGTH`
for the runtime settings.

Then run the batch launcher:

```bash
bash run_batch_aoeb.sh
```

The shell wrappers use `PYTHON_BIN=${PYTHON_BIN:-python}`. For example,
`PYTHON_BIN=python bash run_batch_aoeb.sh` selects the Python executable
without editing the script.

Available AOEB-style task configs under `aoeb_ng/tasks/`:

- `MMRC-R-round-it-pair.json`
- `MMRC-R-session-it-pair.json`
- `MMRC-R-session-vision-doc.json`
- `MRMR-design-vd.json`
- `MRMR-design.json`
- `MRMR-negation-vd.json`
- `MRMR-negation.json`
- `MRMR-theorem-vd.json`
- `MRMR-theorem.json`
- `MRMR-traffic-vd.json`
- `MRMR-traffic.json`

## Run MTEB Tasks

For common MTEB runs, edit the defaults at the top of `run_batch_mteb.sh`.
Set `MODEL` for the model or local model path, `TASK_LIST` for the MTEB task
class names, and `OUTPUT_DIR`, `BATCH_SIZE`, `GPU_ID`, `MAX_LENGTH` for the
runtime settings. The script also exposes task prompt switches:
`VISTA_USE_TASK_PROMPT`, `BGE_M3_USE_TASK_PROMPT`,
`BGE_LARGE_USE_TASK_PROMPT`, and `NOMIC_USE_TASK_PROMPT`.

Then run the batch launcher:

```bash
bash run_batch_mteb.sh
```

Available MTEB-style task names:

> Some of these tasks are already included in the MTEB library, while others are custom task classes implemented in `mteb_patch/tasks`.

- `MuSiQueRetrieval`
- `Design2CodeRetrieval`
- `MVRBComposedScreenshotRetrieval`
- `LoCoMoRetrieval`
- `ToolRetRetrieval`
- `MVRBScreenshotRetrieval`
- `ReFocusRetrieval`
- `ChartMimicRetrieval`
- `LongMemEvalRetrieval`
- `DUDERetrieval`
- `BrowseCompPlusRetrieval`
- `BrightRetrieval`
- `TempReasonL1`
- `TempReasonL2Context`
- `TempReasonL2Fact`
- `TempReasonL2Pure`
- `TempReasonL3Context`
- `TempReasonL3Fact`
- `TempReasonL3Pure`
- `SRABenchRetrieval`
- `FreshStackRetrieval`
- `AppsRetrieval`
- `CodeFeedbackMT`
- `CodeFeedbackST`
- `CodeTransOceanContestRetrieval`
- `CodeTransOceanDLRetrieval`
- `CosQARetrieval`
- `StackOverflowQARetrieval`
- `SyntheticText2SQLRetrieval`
