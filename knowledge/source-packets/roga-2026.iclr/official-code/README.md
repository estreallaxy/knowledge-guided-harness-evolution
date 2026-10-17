# ROGA Artifact (Windows)

This repository is a self-contained public artifact for running the ROGA implementation on Windows.

Included:
- `roga/`: ROGA runtime (`main.py`, tool generation/validation, tool manager, evaluator)
- `llm_server/`: local OpenAI-compatible endpoint used by ROGA, backed by OpenRouter
- `benchmarks/SheetCopilot_full/`: bundled SheetCopilot data (`dataset.xlsx`, `task_sheets`, `task_sheet_answers_v2`)
- `requirements.txt`: Python dependencies

## 1. Prerequisites

- Windows 10/11
- Microsoft Excel Desktop (required for official `Pass@1` checker)
- Conda (Anaconda or Miniconda)
- OpenRouter API key

## 2. Setup Environment (PowerShell)

Open PowerShell at artifact root:

```powershell
cd D:\path\to\artifact
conda create -p .\env python=3.11 pip -y
conda activate .\env
python -m pip install -r .\requirements.txt
```

If `conda activate` does not work:

```powershell
conda init powershell
```

Then restart PowerShell.

## 3. Start LLM Server (Terminal A)

```powershell
cd D:\path\to\artifact\llm_server
conda activate ..\env
$env:LLM_PROVIDER="openrouter"
$env:OPENROUTER_API_KEY="<YOUR_OPENROUTER_API_KEY>"
$env:OPENROUTER_MODEL_OVERRIDE="openai/gpt-4.1"
python .\openai_server.py
```

Server endpoint used by ROGA: `http://127.0.0.1:5000/chat/completions`

## 4. Single-Case Smoke Run (Terminal B)

```powershell
cd D:\path\to\artifact
conda activate .\env
python .\roga\main.py `
  --file_path ".\roga\example_sheets\BoomerangSales.xlsx" `
  --instruction "Please read this workbook and tell me all worksheet names. Do not modify the workbook." `
  --context "" `
  --output_dir ".\roga\output\smoke_case" `
  --model_type dev-gpt-41-longco-2025-04-14 `
  --max_step 10 `
  --no_color_print
```

## 5. Run SheetCopilot (Paper Setting)

The paper setting is `model_type=dev-gpt-41-longco-2025-04-14`, `max_step=10`.

```powershell
cd D:\path\to\artifact
conda activate .\env
python .\roga\exp_sheetcopilot.py `
  --dataset_xlsx ".\benchmarks\SheetCopilot_full\dataset.xlsx" `
  --task_sheets_dir ".\benchmarks\SheetCopilot_full\task_sheets" `
  --start_case 1 `
  --end_case 221 `
  --model_type dev-gpt-41-longco-2025-04-14 `
  --max_step 10 `
  --timeout_sec 1200 `
  --output_root ".\roga\output\sheetcopilot_41" `
  --results_dir ".\roga\results\sheetcopilot_41" `
  --case_prefix sheetcopilot
```

## 6. Evaluate Exec@1 and Pass@1

```powershell
cd D:\path\to\artifact
conda activate .\env
python .\roga\eval_sheetcopilot.py `
  --dataset_xlsx ".\benchmarks\SheetCopilot_full\dataset.xlsx" `
  --gt_root ".\benchmarks\SheetCopilot_full\task_sheet_answers_v2" `
  --output_root ".\roga\output\sheetcopilot_41" `
  --results_dir ".\roga\results\sheetcopilot_41" `
  --start_case 1 `
  --end_case 221 `
  --eval_out ".\roga\eval_results\sheetcopilot_41"
```

Main result file:
- `.\roga\eval_results\sheetcopilot_41\sheetcopilot_eval_result.json`

Notes:
- `Exec@1` is always available from run logs.
- `Pass@1` requires Windows Excel COM (`pywin32` + Excel desktop).

## 7. Troubleshooting

- `No module named win32com`:

```powershell
python -m pip install --upgrade pywin32
python -m pywin32_postinstall -install
```

- `pass_at_1` is `null`:
  - Ensure evaluation runs on Windows with Excel desktop installed.
  - Close existing Excel windows and rerun.

- Connection error to `127.0.0.1:5000`:
  - Verify Terminal A is running `openai_server.py`.
  - Verify `OPENROUTER_API_KEY` is set in Terminal A.
