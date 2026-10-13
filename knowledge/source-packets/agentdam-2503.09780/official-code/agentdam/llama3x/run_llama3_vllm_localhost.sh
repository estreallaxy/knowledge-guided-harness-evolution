#!/bin/bash
# Copyright (c) Meta Platforms, Inc. and affiliates.

export USE_AZURE='false';
export OPENAI_API_BASE=http://localhost:7035/v1;

export model=${1:-/tmp/llama3.2-11b-vision-chat/}
export website=${2:-shopping}
export instruction_path=${3:-configs/p_cot_id_actree_3s.json}
export ngpu=${4:-2}
export chat_template=${5:-llama3x/chat_template_llama3.2.jinja}

echo "USE_AZURE: $USE_AZURE"
echo "OPENAI_API_BASE: $OPENAI_API_BASE"
echo "Model: $model"
echo "chat_template: $chat_template"
echo "website: $website"
echo "instruction_path: $instruction_path"
echo "number of gpus: $ngpu"

if ! nc -z localhost 7035; then
  random_id=$(( $RANDOM % 1000 ))
  echo "Server output is redirected to: /tmp/vllm_server_logs_$random_id.out"
  nohup vllm serve --port 7035 \
                   $model \
                   --dtype auto \
                   --api-key EMPTY \
                   --chat-template $chat_template \
                   --tensor-parallel-size $ngpu \
                   --gpu-memory-utilization 0.8 \
                   --max-model-len 24000 \
                   --max-num-seqs 8 \
                   --enforce-eager > /tmp/vllm_server_logs_$random_id.out &
else
  echo "Server is already running"
fi

while ! nc -z localhost 7035; do
    sleep 15
    echo "... still offline"
done

sleep 10

if [[ $instruction_path == *"som"* ]]; then
  action_set_tag=som
  observation_type=image_som
else
  action_set_tag=id_accessibility_tree
  observation_type=accessibility_tree
fi

echo "action_set_tag: $action_set_tag"
echo "observation_type: $observation_type"

python -u run_agentdam.py \
    --instruction_path $instruction_path \
    --result_dir ./results/$website/ \
    --test_config_base_dir=data/wa_format/${website}_privacy/ \
    --model $model \
    --action_set_tag $action_set_tag \
    --observation_type $observation_type \
    --temperature 0 \
    --max_steps 10 \
    --viewport_height 1280 \
    --privacy_test