export VLLM_LOGGING_LEVEL=INFO
export CUDA_VISIBLE_DEVICES=7
python -m vllm.entrypoints.openai.api_server \
    --model /data2/models/Qwen2.5-7B-Instruct \
    --served-model-name qwen2.5-7b \
    --port 8001 \
    --trust-remote-code \
    --tensor-parallel-size 1