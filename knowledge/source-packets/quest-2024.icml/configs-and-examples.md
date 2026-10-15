# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `pyproject.toml`
- `evaluation/LongBench/config/dataset2prompt.json`
- `evaluation/LongBench/config/dataset2maxlen.json`
- `evaluation/LongBench/config/model2maxlen.json`
- `evaluation/LongBench/config/model2path.json`
- `scripts/example_demo.py`
- `scripts/example_textgen.py`

## Upstream command excerpts

```text
git clone --recurse-submodules https://github.com/mit-han-lab/quest
cd quest
```

```text
conda create -yn quest python=3.10
conda activate quest

# Quest
pip install -e .

# Flash-Attention
pip install ninja packaging
pip install flash-attn==2.6.3 --no-build-isolation

# Install CMake (with version >= 3.26.4)
conda install cmake

# build libraft
cd kernels/3rdparty/raft
./build.sh libraft
```

```text
cd kernels
mkdir build && cd build
cmake ..
make -j
```

```text
# This will automatically build and link the operators
cd quest/ops
bash setup.sh
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
