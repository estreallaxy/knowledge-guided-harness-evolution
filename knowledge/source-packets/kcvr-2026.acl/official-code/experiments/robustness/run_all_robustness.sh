#!/bin/bash
# Run all robustness tests

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "=========================================="
echo "Running Robustness Tests"
echo "=========================================="
echo ""

OUTPUT_DIR="experiments/paper_results/robustness"
mkdir -p "$OUTPUT_DIR"

TESTS=("asr_drop_30" "asr_corrupt" "visual_only")

for test in "${TESTS[@]}"; do
    echo "----------------------------------------"
    echo "Running $test..."
    echo "----------------------------------------"
    
    if [ -f "experiments/robustness/${test}.sh" ]; then
        bash "experiments/robustness/${test}.sh"
    else
        echo "⚠ Warning: Script for $test not found, skipping..."
    fi
    
    echo ""
done

echo "=========================================="
echo "All robustness tests complete!"
echo "Results saved to: $OUTPUT_DIR"
echo "=========================================="

