# Exact source anchors

## Selected mechanism

Compose specialist agents, geospatial tools, staged reasoning, and verification into executable scientific workflows.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.3; `paper/paper-iclr2026.txt` marker `===== PDF p.3 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.9; `paper/paper-iclr2026.txt` marker `===== PDF p.9 =====` | Method |
| Results and ablations | PDF p.6; `paper/paper-iclr2026.txt` marker `===== PDF p.6 =====` | analysis |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/agent/tools/utils.py:5` | `read_image` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/tools/utils.py:21` | `read_image_uint8` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/tools/utils.py:47` | `get_geotransform` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/tools/Perception.py:35` | `threshold_segmentation` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/tools/Perception.py:82` | `bbox_expansion` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/tools/Perception.py:126` | `count_above_threshold` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/tools/Analysis.py:41` | `compute_linear_trend` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/tools/Analysis.py:101` | `mann_kendall_test` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/tools/Analysis.py:190` | `sens_slope` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/tools/Index.py:17` | `calculate_ndvi` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/tools/Index.py:78` | `calculate_batch_ndvi` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/tools/Index.py:101` | `calculate_ndwi` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/tools/Inversion.py:44` | `band_ratio` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/tools/Inversion.py:152` | `lst_single_channel` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/tools/Inversion.py:245` | `lst_multi_channel` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/tools/Statistics.py:32` | `coefficient_of_variation` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/tools/Statistics.py:82` | `skewness` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/tools/Statistics.py:148` | `kurtosis` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `ca1dfaef750654331308a434966d307f1728fd90`. Paper page numbers refer to the fixed local proceedings PDF.
