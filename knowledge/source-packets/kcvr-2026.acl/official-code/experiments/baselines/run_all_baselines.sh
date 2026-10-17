#!/bin/bash
# Run all baseline comparisons

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "=========================================="
echo "Running Baseline Comparisons"
echo "=========================================="
echo ""

OUTPUT_DIR="experiments/paper_results/baselines"
mkdir -p "$OUTPUT_DIR"

BASELINES=("gpt4o_zero_shot" "internvl_zero_shot" "internvl_sft_no_planning" "videollama2_sft" "text_rag")

for baseline in "${BASELINES[@]}"; do
    echo "----------------------------------------"
    echo "Running $baseline..."
    echo "----------------------------------------"
    
    if [ -f "src/baselines/${baseline}.py" ]; then
        python "src/baselines/${baseline}.py" \
            --dataset data/splits/v2_7subj_trainvaltest.json \
            --split test \
            --output-dir "$OUTPUT_DIR/$baseline"
    else
        echo "⚠ Warning: Script for $baseline not found, skipping..."
    fi
    
    echo ""
done

echo "=========================================="
echo "All baseline comparisons complete!"
echo "Results saved to: $OUTPUT_DIR"
echo "=========================================="

