#!/usr/bin/env bash
# score_all.sh
# Run skythought score for a range of token budgets over one or more base directories.

set -euo pipefail       # exit on error & undefined vars

### --- CONFIGURE HERE ---
# (1) Task name
TASK="aime25_2"

# (2) List your base directories here:
BASE_DIRS=(
  "results/your_model_task_dir"
  # add more as needed...
)

# (3) Token budgets
BUDGETS=(2000 6000 10000 14000 18000 22000 26000 30000)
### ---

for BASE_DIR in "${BASE_DIRS[@]}"; do
  for TOKENS in "${BUDGETS[@]}"; do
    RUN_DIR="${BASE_DIR}/truncate_${TOKENS}"
    echo "Scoring token budget ${TOKENS} in ${BASE_DIR} ..."
    skythought score --task "${TASK}" --run-dir "${RUN_DIR}"
  done
done

echo "All scoring runs completed."
