# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `fact_data/data_example.json`

## Upstream command excerpts

```text
fact_code/filter_claim_data.py
```

```text
fact_code/Gx_Px_Ix_Cx.py
```

```text
---

## Contact

If you have any questions about the paper or the code, feel free to contact: `hcwang@ir.hit.edu.cn`.
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
