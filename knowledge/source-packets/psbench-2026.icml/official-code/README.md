# PSBench

PSBench is a benchmark for evaluating GUI agents on image-editing tasks in Adobe Photoshop. It contains 600 tasks that cover a broad range of practical editing operations and visual outcomes. The PSBench paper, **“PSBench: Editing Image via GUI Agents in Photoshop,” has been accepted to ICML 2026**.

For evaluation stability and reproducibility, PSBench uses task-specific, rubric-based LLM-as-a-judge evaluation.

## Adobe Photoshop Requirement

Adobe Photoshop is commercial software and is not included with PSBench. Users must purchase or otherwise obtain a valid Adobe Photoshop license and install the application themselves.

PSBench currently targets Windows, and we recommend **Adobe Photoshop 2024** for the most consistent behavior.

## Task Contents

Each task is stored in `tasks/<id>/` and contains four core files:

- `<id>.json`: the task instruction and metadata, including the configured input and reference filenames.
- `<id>_rubric.json`: task-specific criteria used by the multimodal LLM judge to evaluate visible effects in the final result.
- START image: the source image given to the agent. Its exact filename and extension are declared by `resources.input_file` in the task JSON.
- END image: an author-created successful result used to develop and validate the rubric. Its exact filename and extension are declared by `reference_output.expected_file`. It is not sent to the runtime judge.

Tasks collected from YouTube tutorials also include the corresponding original video file in the task directory.

Example:

```text
tasks/
`-- 001/
    |-- 001.json
    |-- 001_rubric.json
    |-- 001_start.jpg
    `-- 001_end.jpg
```

## System Requirements

- Windows 10 or Windows 11
- Adobe Photoshop installed and activated; Photoshop 2024 is recommended
- A primary display configured to **1920 x 1080**
- Windows display scaling configured to **100%**

The active display resolution must match the configured PSBench screen dimensions. Photoshop should run on the primary display.

## Installation

Clone the source-code repository and enter the project directory:

```powershell
git clone https://github.com/zyn1216/PSBench.git
cd PSBench
```

Create and activate a Conda environment:

```powershell
conda create -n psbench python=3.10 -y
conda activate psbench
```

Install the required Python packages:

```powershell
pip install -r requirements.txt
```

Install the Hugging Face command-line client and download the complete PSBench task package from [`zyn1216/PSBench`](https://huggingface.co/datasets/zyn1216/PSBench):

```powershell
pip install -U huggingface_hub
hf download zyn1216/PSBench --repo-type dataset --local-dir tasks --exclude "README.md" ".gitattributes"
```

The downloaded directory must have the following layout:

```text
PSBench/
|-- tasks/
|   |-- 001/
|   |-- 002/
|   |-- ...
|   `-- 600/
|-- run.py
`-- ...
```

The Hugging Face dataset contains all task JSON files, rubrics, START images, END images, and the original videos associated with YouTube-derived tasks.

## API Configuration

### Claude Computer Use

PSBench requires an Anthropic API account and a Claude model with the Computer Use tool enabled. Follow the [official Claude Computer Use documentation](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool) before running the benchmark.

Set the official Anthropic API key and Claude Computer Use model:

```powershell
$env:ANTHROPIC_API_KEY = "YOUR_ANTHROPIC_API_KEY"
$env:CLAUDE_MODEL = "YOUR_CLAUDE_COMPUTER_USE_MODEL"
```

### Multimodal LLM Judge

Create an API key on the [official OpenAI platform](https://platform.openai.com/api-keys), then set the key and multimodal judge model:

```powershell
$env:OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
$env:PSBENCH_JUDGE_MODEL = "gpt-5.4"
```

PSBench uses the official OpenAI API endpoint by default.

### Photoshop Executable

Set the exact Photoshop executable path. The following is a typical Photoshop 2024 installation path; adjust it for your machine:

```powershell
$env:PHOTOSHOP_EXECUTABLE = "C:\Program Files\Adobe\Adobe Photoshop 2024\Photoshop.exe"
```

Configure the display dimensions used for coordinate mapping:

```powershell
$env:PSBENCH_SCREEN_WIDTH = "1920"
$env:PSBENCH_SCREEN_HEIGHT = "1080"
```

PowerShell environment variables apply only to the current terminal session unless they are configured persistently by the user.

## Running the Benchmark

Before starting a benchmark run, make sure that no Photoshop process from a previous session is still running or shutting down:

```powershell
Get-Process Photoshop -ErrorAction SilentlyContinue
```

The command should produce no output. If a Photoshop process is listed, close Photoshop normally, wait until the process has fully exited, and run the check again before starting PSBench. Make sure that any personal documents are saved before closing Photoshop.

Run one task:

```powershell
python run.py --task-filter 001
```

The standalone single-task entry point is also available:

```powershell
python run_single_example.py --task-path tasks\001
```

Run several selected tasks:

```powershell
python run.py --task-filter 001 051 101
```

Run all 600 tasks:

```powershell
python run.py
```

The exact Photoshop executable may also be supplied for a single run:

```powershell
python run.py `
  --task-filter 001 `
  --photoshop-executable "C:\Program Files\Adobe\Adobe Photoshop 2024\Photoshop.exe"
```

PSBench runs tasks sequentially. Do not run multiple agents against the same interactive Photoshop desktop at the same time.

## Evaluation

Every task has an independent visible-result rubric. The multimodal judge receives:

- the task instruction;
- the task-specific rubric;
- the START image; and
- the candidate RESULT image.

The runtime judge does not receive the END reference image and does not inspect Photoshop layers, masks, adjustment layers, editing history, or other internal document structure. Evaluation reports contain a final pass/fail result and an English explanation, without a numeric score.

## License

PSBench is released under the [MIT License](LICENSE).

## Citation

If you use PSBench in your research, please cite:

```bibtex
@inproceedings{
  zhang2026psbench,
  title={{PSB}ench: Editing Image via {GUI} Agents in Photoshop},
  author={Yinuo Zhang and Zian Cheng and Ziya Zhao and Zongyu Li and Bingshuo Liu and Qingbin Liu and Junxian Cai and Xi Chen and Zhiying Tu and Dianhui Chu and Xiaoyan Yu and Dianbo Sui},
  booktitle={Forty-third International Conference on Machine Learning},
  year={2026},
  url={https://openreview.net/forum?id=O93cZGxYB1}
}
```
