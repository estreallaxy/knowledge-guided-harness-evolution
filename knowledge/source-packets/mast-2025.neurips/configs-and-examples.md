# Configs and examples

# Run the preconditions #

The official repository does not have YAML or configuration file, nor does it have a command line entry. The only program that can be executed is`official-code/llm_judge_pipeline.ipynb`, with all parameters coded hard in Notebook. Run it requires:

|Preconditions|Annotations|
| --- | --- |
|Python Environment|Notebook recorded kernelspec as`multiagent`(Python 3.11.9).|
|OpenAI client and key|`from openai import OpenAI`(`:13`) is filled by `openai_api_key = "KEY"` (`:16`) and the client is set up at `:17-19`; the paper is in o1.|
|MAST Text Materials|`taxonomy_definitions_examples/definitions.txt`and `examples.txt`, provided with the source package, nottebook read in relative path.|
|To be marked|Notebook is`YOUR_TRACE_FILE.txt`/`YOUR_OTHER_TRACE_FILE.txt`(`:127-131`); real track is in an unincorporated `traces/` data set.|

# Official configuration entry (hard code)

|Settings|Value|Location|
| --- | --- | --- |
|Note Model| `model='o1'` | `official-code/llm_judge_pipeline.ipynb:27` |
|Sample temperature| `temperature=1.0` | `official-code/llm_judge_pipeline.ipynb:28` |
|Single entry limit|1,048,570 Character, when exceeding press `1048570 - len(examples)` to cut from the tail| `official-code/llm_judge_pipeline.ipynb:158-159` |
|Resume from checkpoints|Write each item to `saved_results/o1_results_checkpoint.pkl`; save another backup every 10 items| `official-code/llm_judge_pipeline.ipynb:165-181` |
|Failure is wrong.|Once caught, continue, and the results are set.| `official-code/llm_judge_pipeline.ipynb:162-181` |
|Result grouping|`source_sizes = [30,30,30]`equals all sources by long slices of fixed blocks| `official-code/llm_judge_pipeline.ipynb:305-307` |

Notebook starts with traces of`NousResearch/Meta-Llama-3-8B-Instruct`and `base_url="http://localhost:8000/v1"` (`:10-11`, not used for subsequent code); both the paper and the Table 2 report model are OpenAI o1.

# The official process entrance

```text
cell 0  (:3-96)     Define openai_evaluator: trace + MAST definitions + few-shot examples → A summary / B task completion / C yes-no labels for fourteen patterns
cell 1  (:98-105)   Read taxonomy_definitions_examples/examples.txt
cell 4  (:123-133)  Load the list of traces to annotate
cell 6  (:144-182)  Invoke the evaluator item by item and persist checkpoints
cell 8  (:193-282)  parse_responses: parse free text into 0/1 values for 14 patterns
cell 10 (:301-350)  Group by source_sizes and aggregate each source's failure rate
```

The minimum usage method (Appendix C, PDF p. 28) gives the library interface, not the notebook:

```python
!pip install agentdash
from agentdash import annotator
MASTAnnotator = annotator("your-api-key")
mast_annotation = MASTAnnotator.produce_taxonomy(trace)
mast_annotation["failure_modes"]      # {pattern id: whether matched}
MASTAnnotator.get_failure_mode_info("1.1")
mast_annotation["summary"], mast_annotation["task_completion"], mast_annotation["total_failures"]
```

The`agentdash`package is not in the code snapshot of the source package and is not installed or called for validation.

# Data portal

|Entry|Location|Status|
| --- | --- | --- |
| MAST-Data（Hugging Face） |Footnote 2 (PDF p.1) to`https://huggingface.co/datasets/mcemri/MAST-Data`|dissertation; not downloaded.|
|MAD dataset|Repository`README.md:15-42`and `traces/README.md` point to `https://huggingface.co/datasets/mcemri/MAD`, containing`MAD_full_dataset.json`(LLLM label) and `MAD_human_labelled_dataset.json` (manual label)|Repository writing; two entries are not consistent with the footnote to the paper and no valid current repository has been verified.|
|Repository`traces/`|Upstream, there are 13359 files under HEAD, divided into`AG2`(7184), `MagenticOne_GAIA` (4535), `math_interventions` (600), `HyperAgent` (513), `programdev` (389), `mmlu` (91), `OpenManus_GAIA` (30), `AppWorld` (16)|Not included in this source package.|
|ProgrammeDev Job List|`traces/programdev/programdev_dataset.json` (dissertation Appendix D footnote 3 Quote this path)|Not included in this source package.|

# Local Save Range

`official-code/`(13 files, 893,860 byte ≈ 0.85 MB):

|Contents|Documentation|
| --- | --- |
|Classification and Example| `taxonomy_definitions_examples/definitions.txt`、`examples.txt` |
|Mark current lines| `llm_judge_pipeline.ipynb` |
|Consistency label original table|4 PDFs for`inter_annotator_agreement_annotations/`(total 272,379 bytes)|
|Repository entrance| `README.md` |
|README Reference Chart| `assets/taxonomy_v11_cropped-1.png`、`taxonomy_v11_cropped.pdf`、`arxiv_figure_v2_cropped-1.png`、`arxiv_figure_v2_cropped.pdf`、`mas22.jpg` |

Not explicitly included:

|Not included|Reason|
| --- | --- |
|`traces/`(13359 files)|is a data set and is much larger than the budget of the source package; obtained from the Hugging Face entry above.|
| `assets/mast_logo_with_writing.png`（1.37 MB） |A logo of more than 1 MB each.|
|Root`LICENSE`|This document is not available in the upstream root directory (the tree of HEAD has been checked).|
|Experiment Output, API Key|repository does not exist;notebook key is the placeholder.|

Snapshot fixed upstream review`a70542e541b2104ef8fcd785778179e173fb8d70`, except for the above logo.
