#!/bin/bash

BASE_DIR="checkpoints/new_data/amem"
export OPENAI_API_KEY=""
TARGET_PATTERN=""
TARGET_PATTERN2=""

# iterate json files in the directory
for RETRIEVAL_FILE in $BASE_DIR/*.json; do
    # skip if not matching target pattern if specified
    if [[ -n "$TARGET_PATTERN" && "$RETRIEVAL_FILE" != *"$TARGET_PATTERN"* ]]; then
        continue
    fi
    echo "Processing retrieval file: $RETRIEVAL_FILE"
    
    # run generation
    python clonemem_adaptation/eval/run_generation.py \
        --input_file="data/new_data/all_users_benchmark_en.json" \
        --retrieval_file="$RETRIEVAL_FILE" \
        --top_k=5 \
        --model_name="gpt-4o-mini" \
        --api_key="$OPENAI_API_KEY" \
    #     --model_name=meta-llama/Meta-Llama-3.1-8B-Instruct \

    python clonemem_adaptation/eval/run_generation.py \
        --input_file="data/new_data/all_users_benchmark_en.json" \
        --retrieval_file="$RETRIEVAL_FILE" \
        --top_k=10 \
        --model_name="gpt-4o-mini" \
        --api_key="$OPENAI_API_KEY" \
    #     --model_name=meta-llama/Meta-Llama-3.1-8B-Instruct \

    python clonemem_adaptation/eval/run_generation.py \
        --input_file="data/new_data/all_users_benchmark_en.json" \
        --retrieval_file="$RETRIEVAL_FILE" \
        --top_k=20 \
        --model_name="gpt-4o-mini" \
        --api_key="$OPENAI_API_KEY" \
        # --model_name=meta-llama/Meta-Llama-3.1-8B-Instruct \

    # # run auto metrics
    python clonemem_adaptation/eval/compute_auto_metrics_for_clonemem.py \
        --in_file="$RETRIEVAL_FILE" \
        --qa_file="data/new_data/all_users_benchmark_en.json"
done

TARGET_PATTERN2="top20"
GENERATION_DIR="$BASE_DIR/generation_results"
for GEN_FILE in $GENERATION_DIR/*.json; do
    # skip if not matching target pattern if specified
    if [[ -n "$TARGET_PATTERN" && "$GEN_FILE" != *"$TARGET_PATTERN"* ]]; then
        continue
    fi
    if [[ -n "$TARGET_PATTERN2" && "$GEN_FILE" != *"$TARGET_PATTERN2"* ]]; then
        continue
    fi

    echo "Processing generation file: $GEN_FILE"
    # run llm metrics
    python clonemem_adaptation/eval/compute_llm_metrics_for_clonemem.py \
        --qa_file="data/new_data/all_users_benchmark_en.json" \
        --gen_file="$GEN_FILE" \
        --api_key="$OPENAI_API_KEY" \
        --eval_qa \
        --eval_mem="mem"
done