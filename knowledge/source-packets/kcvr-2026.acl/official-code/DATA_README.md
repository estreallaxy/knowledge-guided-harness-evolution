# Data Format and Examples

This document describes the data format used in KCVR and provides example data for the `math` subject.

## Knowledge Graph

The knowledge graph is stored in CSV format under `knowledge_graph/raw_csv/`:

- `nodes_kc.csv`: Knowledge Concept nodes
- `nodes_tp.csv`: Teaching Point nodes  
- `relations.csv`: Relations between nodes (BASED_ON, NEXT, etc.)

Example data for the `math` subject is provided (50 KCs, 20 TPs, 30 relations).

## Annotations

Standardized annotations are stored in `data/annotations/standard_labels/`:

- `micro/`: Segment-level annotations
  - Format: `{subject}/{video_id}__{segment_id}.json`
  - Fields: `summary_gt`, `objectives_gt`, `transcript`, etc.
- `macro/`: Full-video annotations
  - Format: `{subject}/{video_id}_global.json`
  - Fields: `summary_edu`, `overall_summary`, etc.

Example annotations for the `math` subject are provided (~10% of full dataset).

## Plans

Generated plans are stored in `cache/plans/`:

- `micro_plans/`: Segment-level knowledge plans
  - Format: `{subject}/{video_id}/{video_id}__seg_{suffix}.json`
  - Contains: `kc_nodes`, `tp_nodes`, `pi` (progression path), `edges_based_on`, etc.
- `macro_gks/`: Global Knowledge Sketch for full videos
  - Format: `{subject}/{video_id}/{video_id}_gks.json`

Example plans for the `math` subject are provided (~10% of full dataset).

## Splits

Data splits are defined in JSON format under `data/splits/`:

```json
{
  "meta": {
    "version": "v2",
    "seed": 42,
    "train_ratio": 0.7,
    "val_ratio": 0.15,
    "test_ratio": 0.15
  },
  "splits": {
    "subject_name": {
      "train": ["video_id1", "video_id2", ...],
      "val": [...],
      "test": [...]
    }
  }
}
```

## Frames

Video frames are extracted and stored in `cache/frames/`:

- Format: `{video_id}/{segment_id}/000.jpg` to `007.jpg` (8 frames per segment)
- Images are uniformly sampled from each segment

Note: Frame images are not included in this repository due to size constraints.

## Usage

To use the example data:

1. Knowledge graph files are ready to use in `knowledge_graph/raw_csv/`
2. Example annotations can be found in `data/annotations/standard_labels/micro/math/`
3. Example plans are in `cache/plans/micro_plans/math/`

For full dataset, please refer to the paper or contact the authors.

