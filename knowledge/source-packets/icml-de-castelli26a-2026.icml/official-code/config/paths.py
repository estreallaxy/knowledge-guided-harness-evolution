import os

PROJECT_FOLDER_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATASET_PATH = os.path.join(PROJECT_FOLDER_PATH, "data")
RAW_DATA_PATH = os.path.join(DATASET_PATH, "raw")
PYG_DATA_PATH = os.path.join(DATASET_PATH, "pyg")
RAW_SNAPSHOTS_PATH = os.path.join(RAW_DATA_PATH, "snapshots")

# Project-wide root for *downloaded* datasets (Hugging Face, SNAP, ...). Each
# dataset gets its own subfolder under this root, so several datasets can share
# it. Defaults to the repository's data/ folder; override with the
# LAMP_DATA_ROOT env var (e.g. to point at a shared storage volume).
DATA_ROOT = os.environ.get("LAMP_DATA_ROOT", DATASET_PATH)

# Colored Leaf Counting (CLC) is downloaded (read-only) from the Hugging Face Hub
# into <DATA_ROOT>/ColoredLeafCounting/ in its compact format:
#   spider.pt   and   <config>/{data.pt, splits.json}
CLC_PATH = os.path.join(DATA_ROOT, "ColoredLeafCounting")
PYG_NODE_PREDICTION_DATASET_PATH = os.path.join(PYG_DATA_PATH, "node_prediction")
PYG_LINK_PREDICTION_PATH = os.path.join(PYG_DATA_PATH, "link_prediction")

EXPERIMENTS_PATH = os.path.join(PROJECT_FOLDER_PATH, "experiments")
INFO_PATH = os.path.join(PROJECT_FOLDER_PATH, "info")

CONFIGURATIONS_PATH = os.path.join(PROJECT_FOLDER_PATH, "configurations")
DATASET_SPECIFIC_HYPERPARAMETERS_PATH = os.path.join(CONFIGURATIONS_PATH, "datasets")
# Model hyperparameter grids (paper-canonical configs) live under configurations/.
TUNING_HYPERPARAMETERS_PATH = os.path.join(CONFIGURATIONS_PATH, "hyperparameters")
