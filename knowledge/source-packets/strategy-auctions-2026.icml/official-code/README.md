# HST-Bench

HST-Bench is a dataset released as part of the paper
[Scaling Small Agents Using Strategy Auctions](https://arxiv.org/pdf/2602.02751) under the
[CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) license.

The benchmark covers two task categories:

- **Coding** — `hst_bench_coding.csv`
- **Deep search** — `hst_bench_deep_search.csv`

Each task originates from a public host dataset. To respect the licenses of
those host datasets, the CSVs shipped here contain only task metadata
(`task_id`, `origin_dataset`, `origin_dataset_id`, `avg_human_completion_time`)
— **not** the question/answer content. The enrichment scripts below reconstruct
the full task content by pulling the original fields from each host dataset and
adding `question`, `correct_answer` (and, for coding, `tests`) columns.

## Setup

```bash
pip install -r requirements.txt
```

A few host datasets are gated on HuggingFace (e.g. GAIA, HLE). To enrich those,
request access on each dataset's page and authenticate with a token via
`HF_TOKEN` or `huggingface-cli login`. Without a token, gated rows are left
blank and the rest still process.

## Usage

Enrich the deep-search tasks:

```bash
python3 enrich_search_tasks.py \
    --input hst_bench_deep_search.csv \
    --output hst_bench_deep_search_enriched.csv
```

Enrich the coding tasks (`coding_mcq.csv` is bundled and read locally):

```bash
python3 enrich_coding_tasks.py \
    --input hst_bench_coding.csv \
    --output hst_bench_coding_enriched.csv
```

## Host datasets

**Deep search** (`enrich_search_tasks.py`):

| origin_dataset | source |
| --- | --- |
| PopQA | [akariasai/PopQA](https://huggingface.co/datasets/akariasai/PopQA) |
| SimpleQA | [basicv8vc/SimpleQA](https://huggingface.co/datasets/basicv8vc/SimpleQA) |
| HotpotQA | [hotpotqa/hotpot_qa](https://huggingface.co/datasets/hotpotqa/hotpot_qa) |
| Humanity's Last Exam | [cais/hle](https://huggingface.co/datasets/cais/hle) (gated) |
| GAIA | [gaia-benchmark/GAIA](https://huggingface.co/datasets/gaia-benchmark/GAIA) (gated) |

**Coding** (`enrich_coding_tasks.py`):

| origin_dataset | source |
| --- | --- |
| coding_mcq | `coding_mcq.csv` (local) |
| MBPP | [Muennighoff/mbpp](https://huggingface.co/datasets/Muennighoff/mbpp) |
| LeetCodeDataset | [newfacade/LeetCodeDataset](https://huggingface.co/datasets/newfacade/LeetCodeDataset) |

## License

HST-Bench is released under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/).
See the `LICENSE` file. Note that the host datasets are governed by their own
licenses and terms of use.
