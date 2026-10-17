# SPDX-FileCopyrightText: Copyright (c) 1993-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
OBCACHE_ROOT = CURRENT_DIR.parent
for path in (str(OBCACHE_ROOT), str(CURRENT_DIR)):
    if path not in sys.path:
        sys.path.insert(0, path)

from benchmarks.longbench.calculate_metrics import calculate_metrics as longbench_scorer
from benchmarks.longbench.calculate_metrics import calculate_metrics_e as longbench_scorer_e
from benchmarks.ruler.calculate_metrics import calculate_metrics as ruler_scorer

from kvpress import (
    AdaKVPress,
    OBCacheH2OPress,
    OBCachePyramidKVPress,
    OBCacheSnapKVPress,
    OBCacheTOVAPress,
    SnapKVPress,
    StreamingLLMPress,
)

# These dictionaries define the available datasets, scorers, and KVPress methods for evaluation.
DATASET_REGISTRY = {
    # "ruler": "simonjegou/ruler",
    "ruler": "tracygu/ruler",
    "longbench": "Xnhyacinth/LongBench",
    "longbench-e": "Xnhyacinth/LongBench",
}

SCORER_REGISTRY = {
    "ruler": ruler_scorer,
    "longbench": longbench_scorer,
    "longbench-e": longbench_scorer_e,
}


PRESS_REGISTRY = {
    "h2o": OBCacheH2OPress(pruning_score="attn"),
    "obcache_v_h2o": OBCacheH2OPress(pruning_score="obcache-v"),
    "obcache_vL1_h2o": OBCacheH2OPress(pruning_score="obcache-vL1"),
    "obcache_k_h2o": OBCacheH2OPress(pruning_score="obcache-k"),
    "obcache_vk_h2o": OBCacheH2OPress(pruning_score="obcache-vk"),

    "tova": OBCacheTOVAPress(pruning_score="attn"),
    "obcache_v_tova": OBCacheTOVAPress(pruning_score="obcache-v"),
    "obcache_k_tova": OBCacheTOVAPress(pruning_score="obcache-k"),
    "obcache_vk_tova": OBCacheTOVAPress(pruning_score="obcache-vk"),

    "snapkv": SnapKVPress(),
    "obcache_v_snapkv": OBCacheSnapKVPress(pruning_score="obcache-v"),
    "obcache_k_snapkv": OBCacheSnapKVPress(pruning_score="obcache-k"),
    "obcache_vk_snapkv": OBCacheSnapKVPress(pruning_score="obcache-vk"),

    "adakv_snapkv": AdaKVPress(SnapKVPress()),
    "adakv_obcache_v_snapkv": AdaKVPress(OBCacheSnapKVPress(pruning_score="obcache-v")),
    "adakv_obcache_vL1_snapkv": AdaKVPress(OBCacheSnapKVPress(pruning_score="obcache-vL1")),
    "adakv_obcache_k_snapkv": AdaKVPress(OBCacheSnapKVPress(pruning_score="obcache-k")),
    "adakv_obcache_vk_snapkv": AdaKVPress(OBCacheSnapKVPress(pruning_score="obcache-vk")),

    "obcache_v_pyramidkv": OBCachePyramidKVPress(pruning_score="obcache-v"),
    "obcache_k_pyramidkv": OBCachePyramidKVPress(pruning_score="obcache-k"),
    "obcache_vk_pyramidkv": OBCachePyramidKVPress(pruning_score="obcache-vk"),

    "streaming_llm": StreamingLLMPress(),
    "no_press": None,
}
