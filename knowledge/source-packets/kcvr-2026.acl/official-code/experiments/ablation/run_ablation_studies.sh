#!/bin/bash
# Run all ablation studies (B0-B6)
# This script runs all ablation variants sequentially

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "=========================================="
echo "Running Ablation Studies"
echo "=========================================="
echo ""

# Create output directory
OUTPUT_DIR="experiments/paper_results/ablation"
mkdir -p "$OUTPUT_DIR"

# Run each variant
VARIANTS=("B0_baseline" "B1_ctl_only" "B2_text_rag" "B3_planner" "B4_kgva" "B5_acp_s3d" "B6_full")

for variant in "${VARIANTS[@]}"; do
    echo "----------------------------------------"
    echo "Running $variant..."
    echo "----------------------------------------"
    
    if [ -f "experiments/ablation/${variant}.sh" ]; then
        bash "experiments/ablation/${variant}.sh"
    else
        echo "⚠ Warning: Script for $variant not found, skipping..."
    fi
    
    echo ""
done

echo "=========================================="
echo "All ablation studies complete!"
echo "Results saved to: $OUTPUT_DIR"
echo "=========================================="

