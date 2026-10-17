#!/bin/bash

source /data2/miniconda3/envs/wildbench/bin/activate wildbench

# 这里的环境变量对 agent 引擎可能不直接生效，因为推理在 server 端
# 但建议保留以防脚本内部加载 tokenizer
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,6

# 配置参数
MODEL_NAME="qwen-kto"  
MODEL_PRETTY_NAME="FeedbackAgent-llama-kto2" 
LOCAL_API_BASE="http://localhost:8010/v1" 
OUTPUT_DIR="result_dirs/wild_bench_v2/"
SHARDS_DIR="${OUTPUT_DIR}/tmp_${MODEL_PRETTY_NAME}"

# 采样参数
TEMP=0
TOP_P=1.0
MAX_TOKENS=4096 # 建议调小一点，避免 8192 上下文溢出

# 并行分片配置
n_shards=3           # 改为 4 个并行
total_examples=1024
shard_size=$((total_examples / n_shards))

# 检查服务
echo "测试 vLLM API 连接..."
curl -s http://localhost:8010/v1/models > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "✗ 无法连接到 vLLM API 服务，请检查端口 8010"
    exit 1
fi

mkdir -p $SHARDS_DIR

echo "开始并行推理，共 $n_shards 个分片..."

for ((i = 0; i < $n_shards; i++)); do
    start=$((i * shard_size))
    # 最后一个分片确保覆盖到最后
    if [ $i -eq $((n_shards - 1)) ]; then
        end=1024
    else
        end=$((start + shard_size))
    fi

    echo "启动分片 $i: Index $start 到 $end"
    
    # 后台运行
    python src/unified_infer.py \
        --engine agent \
        --model_name $MODEL_NAME \
        --model_pretty_name $MODEL_PRETTY_NAME \
        --download_dir $LOCAL_API_BASE \
        --data_name wild_bench \
        --start_index $start \
        --end_index $end \
        --temperature $TEMP \
        --top_p $TOP_P \
        --max_tokens $MAX_TOKENS \
        --output_folder $SHARDS_DIR & 
done

# 等待所有后台进程结束
wait

echo "所有分片完成，正在合并结果..."

# 合并 JSON 文件
# 注意：确保你的 src 目录下有这个 merge_results.py
python src/merge_results.py $SHARDS_DIR $MODEL_PRETTY_NAME

# 将合并后的文件移动到正式目录
cp "$SHARDS_DIR/${MODEL_PRETTY_NAME}.json" "$OUTPUT_DIR/${MODEL_PRETTY_NAME}.json"

echo "================================================================"
echo "Inference completed!"
echo "Output file: $OUTPUT_DIR/${MODEL_PRETTY_NAME}.json"
echo "================================================================"
echo ""
echo "Next steps:"
echo "1. 运行评估："
echo "   cd evaluation && bash run_eval_v2_instant.score.sh gpt-4o $MODEL_PRETTY_NAME"
echo ""
echo "2. 查看结果："
echo "   cd leaderboard && bash show_eval.sh"

