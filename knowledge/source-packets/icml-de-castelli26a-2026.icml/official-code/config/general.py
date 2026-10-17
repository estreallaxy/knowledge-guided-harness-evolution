"""This script contains the project configuration."""

import numpy as np
import random
import torch


def set_seed(seed: int):
    """Set the random seed for reproducibility."""
    np.random.seed(seed)
    random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


# region seed
GLOBAL_SEED = 1029384756
# endregion

DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"

N_REINIT = 10
