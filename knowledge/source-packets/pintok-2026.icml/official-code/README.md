# PinTok

PinTok is a high‑performance tokenizer. We implement it using a high‑speed packet/compute path under the hood (DPDK is just the implementation method). Code and env vars still use “dpdk” names, but PinTok is the system you use and benchmark.

## Build

- Prereqs: `libdpdk` (pkg‑config), GCC/Clang, Meson/Ninja, Python 3.9+.
- One‑time setup: `sudo ./setup_dpdk.sh` (hugepages).
- Build: `meson setup build && meson compile -C build`.
- Python package (enables `import pintok`): `pip install -e .` from the repo root.
- Optional (plots/datasets): `pip install -r src/python/requirements.txt matplotlib datasets`.

## Plug‑and‑Play Usage (pintok)

PinTok mirrors standard tokenizer pipeline usage:

```python
from pintok import PinTokPipeline

pipeline = PinTokPipeline("gpt2")
pipeline.start()
token_ids = pipeline.tokenize("Hello world!")   # or pipeline("Hello world!")
pipeline.stop()
```

Or as a context manager:

```python
from pintok import pipeline

with pipeline("gpt2") as p:
    token_ids = p("Hello world!")
```

`PinTokPipeline` auto‑discovers the built binary, picks an isolated core (falls
back to core 0 on dev machines), decides sudo vs non‑sudo from hugepage
permissions, and frames/sends UDP packets internally. Everything is overridable
via kwargs (`pin_core=`, `use_sudo=`, `tokenizer_type=`, `root=`) or the usual
`DPDK_*` env vars; set `PINTOK_ROOT` if running from outside the repo without
an editable install. Async use is supported too: `pipeline.send(text)` +
`pipeline.get_result()`. Full example: `src/python/examples/example_pintok.py`.

## Run Experiments (recommended)

- Script: `tests/python/analyze/run_experiments.py` (aggregates runs, writes CSVs/plots under `tests/python/analyze/results/<test-name>/`).
- Minimal PinTok run:
  - `python tests/python/analyze/run_experiments.py --mode dpdk --tokenizer bpe --model modernbert-base --runs 3 --max-packets 20 --dataset openwebtext --tokens-per-packet 512 --test-name demo --override --pin-core 0`
- Full comparison:
  - `python tests/python/analyze/run_experiments.py --mode all --tokenizer bpe --model gpt2 --runs 5 --max-packets 50 --dataset all --tokens-per-packet 128 256 512 1024 2048 --test-name paper_like --override --pin-core 0`
- Key flags: `--mode {dpdk|rust|python|embed|all}`, `--dataset {simple|openwebtext|multilingual|code}`, `--tokens-per-packet ...`, `--latency-mode tokenize-only|end2end`, `--allow-non-isolated` (dev only).
- Outputs: `results_summary.csv`, `throughput_summary.csv`, per‑metric plots; plus `cache_summary.csv` for PinTok caches.

## Quick Check

- Interactive runner: `tests/python/analyze/run_tokenizer.py`.
- Example: `python tests/python/analyze/run_tokenizer.py --mode dpdk --tokenizer bpe --model gpt2 --pin-core 0`.
- Send test traffic: `python tests/python/send_packets/send_n_packets.py -n 10 --dataset simple` (UDP 6000).

## Drop‑In Use

- As a service (recommended):
  - Build gives `build/src/dpdk/tokenizer/tokenizer_dpdk_bpe_vm`.
  - Run with core pinning (no NIC needed; uses `--no-pci`):
    - `DPDK_PIN_CORE=0 DPDK_ALLOW_NON_ISOLATED=1 ./build/src/dpdk/tokenizer/tokenizer_dpdk_bpe_vm --no-pci --log-level=3 -- modernbert-base`
  - Send UDP to port 6000 using the extended 16‑byte header: `"TOKN" + seq + total + message_id` (see `tests/python/send_packets/send_n_packets.py`).
  - Parse results between `DPDK_TOKENIZATION_START`/`DPDK_TOKENIZATION_END` on stdout.
- From Python: use `src/python/utils/pipelines.py`:
  - `from utils import DPDKPipeline; p = DPDKPipeline(tokenizer_type="bpe", model="gpt2", pin_core=0, allow_non_isolated=True); p.start(); r = p.get_result(timeout=5.0); p.stop()`.

## Packet Format

- Port: UDP 6000. Header: legacy 8‑byte `(seq,total)` or extended 16‑byte `TOKN + seq + total + message_id` (recommended; enables multiple in‑flight messages).
