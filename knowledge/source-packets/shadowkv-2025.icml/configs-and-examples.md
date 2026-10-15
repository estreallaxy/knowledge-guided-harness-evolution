# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `requirements.txt`
- `setup.py`
- `kernels/main.cu`

## Upstream command excerpts

```text
# create env
conda create -n ShadowKV python=3.10 -y
conda activate ShadowKV

# install packages
pip install -r requirements.txt
pip install flash-attn --no-build-isolation

# nemo dependencies (for dataset building)
pip install wheel
pip install Cython
pip install youtokentome
pip install nemo_toolkit[all]==1.23

# flashinfer
pip install flashinfer -i https://flashinfer.ai/whl/cu121/torch2.3/

# cutlass
mkdir 3rdparty
git clone https://github.com/NVIDIA/cutlass.git 3rdparty/cutlass

# build kernels for ShadowKV
python setup.py build_ext --inplace
```

```text
# build RULER
python -c "import nltk; nltk.download('punkt')"
cd data/ruler
bash create_dataset.sh "gradientai/Llama-3-8B-Instruct-Gradient-1048k" "llama-3"
```

```text
# Full attention
OMP_NUM_THREADS=48 torchrun --standalone --nnodes=1 --nproc_per_node 8 test/eval_acc.py --datalen 131072 --method full --dataset_name "ruler/niah_single_1,ruler/niah_single_2,ruler/niah_single_3,ruler/niah_multikey_1,ruler/niah_multikey_2,ruler/niah_multiquery,ruler/niah_multivalue,ruler/vt,ruler/fwe,ruler/qa_1,ruler/qa_2" --model_name "gradientai/Llama-3-8B-Instruct-Gradient-1048k"

# ShadowKV
OMP_NUM_THREADS=48 torchrun --standalone --nnodes=1 --nproc_per_node 8 test/eval_acc.py --datalen 131072 --method shadowkv --dataset_name "ruler/niah_single_1,ruler/niah_single_2,ruler/niah_single_3,ruler/niah_multikey_1,ruler/niah_multikey_2,ruler/niah_multiquery,ruler/niah_multivalue,ruler/vt,ruler/fwe,ruler/qa_1,ruler/qa_2" --sparse_budget 2048 --rank 160 --chunk_size 8
```

```text
# Full attention with MInference
OMP_NUM_THREADS=48 torchrun --standalone --nnodes=1 --nproc_per_node 8 test/eval_acc.py --datalen 131072 --method full --dataset_name "ruler/niah_single_1,ruler/niah_single_2,ruler/niah_single_3,ruler/niah_multikey_1,ruler/niah_multikey_2,ruler/niah_multiquery,ruler/niah_multivalue,ruler/vt,ruler/fwe,ruler/qa_1,ruler/qa_2" --minference

# ShadowKV with MInference
OMP_NUM_THREADS=48 torchrun --standalone --nnodes=1 --nproc_per_node 8 test/eval_acc.py --datalen 131072 --method shadowkv --dataset_name "ruler/niah_single_1,ruler/niah_single_2,ruler/niah_single_3,ruler/niah_multikey_1,ruler/niah_multikey_2,ruler/niah_multiquery,ruler/niah_multivalue,ruler/vt,ruler/fwe,ruler/qa_1,ruler/qa_2" --sparse_budget 2048 --rank 160 --chunk_size 8 --minference
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
