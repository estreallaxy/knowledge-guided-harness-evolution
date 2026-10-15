# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `requirements.txt`
- `ag_src/agent_utils/config.py`
- `ag_src/agent_utils/run_exp.py`

## Upstream command excerpts

```text
Please put the embedding file under the `data` directory.

The cost of this part is very low, 
less than $1 for all the dataset's relations and questions with the use of cache.

Anyway, If you indeed have any problem in implementing this, please feel free to contact us.

# Run
1. config the hyper-parameters in `agent_utils/config.py`
2. fill the api-key and the KB query endpoint in `agent_utils/config.py`
3. execute `agent_utils/run_exp.py`

# File Structure
```

```text
# Citation
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
