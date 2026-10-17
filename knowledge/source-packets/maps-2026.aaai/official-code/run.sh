#!/bin/sh

EXPERIMENT_NAMES=(
    "mathvista"
    "emma"
    "olympiad_full"
    "olympiad_wo_interpreter"
    "olympiad_wo_aligner"
    "olympiad_wo_scholar"
    "olympiad_wo_critic"
)

ABLATION_MAP=(
    "mathvista:full"
    "emma:full"
    "olympiad_full:full"
    "olympiad_wo_interpreter:wo_interpreter"
    "olympiad_wo_aligner:wo_aligner"
    "olympiad_wo_scholar:wo_scholar"
    "olympiad_wo_critic:wo_critic"
)

print_help() {
    echo "Usage:"
    echo "  ./run.sh [experiment_name]"
    echo "Available experiments:"
    for exp in "${EXPERIMENT_NAMES[@]}"; do
        echo "  $exp"
    done
    exit 1
}

# Parameter check
if [ $# -eq 0 ]; then
    print_help
fi

# Find the matching experiment configuration
found=0
for mapping in "${ABLATION_MAP[@]}"; do
    if [ "$1" = "${mapping%%:*}" ]; then
        dataset=$(echo $1 | cut -d'_' -f1)
        ablation="${mapping#*:}"
        found=1
        break
    fi
done

if [ $found -eq 0 ]; then
    echo "Error: Invalid experiment '$1'"
    print_help
fi

echo "========================================"
echo " Dataset: $dataset"
echo " Ablation setting: $ablation"
echo "========================================"

python3 run.py --dataset $dataset --ablation $ablation