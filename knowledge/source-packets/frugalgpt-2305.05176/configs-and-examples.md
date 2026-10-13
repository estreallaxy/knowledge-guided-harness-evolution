# Configs and examples

The following are taken from`official-code/`(review`2b23e6acbd4b39f71912816640dcc59e45aa4b5e`)** not implemented on this machine.

# Run the preconditions #

|Item|Request|Source|
| --- | --- | --- |
|Install|`pip install git+https://github.com/stanford-futuredata/FrugalGPT`|Upstream README|
|Vendor evidence|Key for multiple commercial LLM API (12 API / 5 suppliers)|Thesis Table 1; this package does not contain supporting documentation|
|Price tables| `config/serviceinfo.json`、`config/serviceidmap.json` |Refillable at current** prices, paper prices are outdated|
|Data|HEADLINES and other data sets (upstream download via wget)|Upstream README; not included in`data/`|

# Upstream Example Command

```bash
git clone https://github.com/stanford-futuredata/FrugalGPT && cd FrugalGPT
pip install git+https://github.com/stanford-futuredata/FrugalGPT

wget https://github.com/lchen001/DataHolder/releases/download/v0.0.1/HEADLINES.zip
unzip HEADLINES.zip -d strategy/
wget -P db/ https://github.com/lchen001/DataHolder/releases/download/v0.0.1/HEADLINES.sqlite
wget -P db/ https://github.com/lchen001/DataHolder/releases/download/v0.0.1/qa_cache.sqlite

# Run the trade-off notebook under examples/ as needed
jupyter notebook examples/FrugalGPT_gen_tradeoff_HEADLINES.ipynb
```

Officially, a Colab demonstration notebook free of API key is also available; the concept can be run without the environment.

Configure Snippet

```json
// Excerpt from config/serviceinfo.json: fields priced by input/output token
"textsynth": {
  "gptneox_20B": { "cost_input": 0.0000014, "cost_output": 0.000035, "cost_fixed": 0, "fixed_size": 0 }
}
```

# Unrecognized entry (identified)

- Default threshold for cascade and "up/up" determination details: 0.37 for the paper is an example from HEADLINES, the code default is not checked.
- Training configuration (models, data volume, cross-reference):`src/FrugalGPT/scoring.py`does not check the settings in Notebook.
- Cost-to-reach-accreditation entry for scripts corresponding to the paper Table 3: not located.
