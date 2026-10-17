# CloneMem Data Generation
---

## Prerequisites
- Python 3.10+
- Neo4j database instance
- OpenRouter API key (or other LLM provider)

---

## Installation

```bash
pip install -e .
```

---

## Configuration

Edit the configuration file at `configs/build.yaml`:

### Environment Variables

Create a `.env` file in the project root:

```
NEO4J_URL=bolt://localhost:7687
NEO4J_PASSWORD=your_password
OPEN_ROUTER_API_KEY=your_api_key
```

### Key Configuration Options

| Option | Description |
|--------|-------------|
| `generation.start_year` | Starting year for the persona's digital traces |
| `generation.duration_years` | Time span of generated data (1-3 years) |
| `person.big_five` | Big Five personality traits (0-1 scale) |
| `run.lang` | Output language: `"zh"` (Chinese) or `"en"` (English) |

---

## Pipeline

The data generation consists of two steps:

### Step 1: Build Data & QA

Generate persona data (digital traces) and initial QA pairs:

```bash
clonemem build --config configs/build.yaml
```

This creates:
- Persona and digital traces stored in Neo4j
- Intermediate QA data in `outputs/`

### Step 2: Postprocessing
Cleaning Data, Run QA verification, MCQ generation, and translation:

```bash
clonemem postprocess \
  --config configs/build.yaml \
  --person-id <person_id> \
  --person-name <person_name>
```

This produces:
- `outputs/benchmark_final_person_id=<id>/`
    - `*_benchmark_en.json` — English benchmark
    - `*_benchmark_zh.json` — Chinese benchmark
    - `*_human_review.json` — For manual review
    - `*_mcq_validation_report.json` — MCQ validation results
    - `*_rejected.json` — Rejected QA pairs

---

## Output Structure

```
outputs/
├── benchmark_final_person_id=<id>/
│   ├── *_benchmark_en.json
│   ├── *_benchmark_zh.json
│   └── ...
└── qa_interval_person_id=<id>/
    └── IntervalQASet_*.json

data/runs/
└── <person_id>_<timestamp>_<hash>/
    ├── token_by_generator.json
    ├── token_by_prompt.json
    ├── token_events.jsonl
    └── token_summary.json    # Token usage statistics
```

---

## CLI Reference

```bash
# Full pipeline: build data and QA
clonemem build --config configs/build.yaml

# Build digital traces only (no QA generation)
clonemem trace-only --config configs/build.yaml

# Build QA only (from existing Neo4j data)
clonemem qa-only --config configs/build.yaml --person-id <person_id>

# Postprocessing
clonemem postprocess --config configs/build.yaml \
  --person-id <person_id> \
  --person-name <person_name>
```