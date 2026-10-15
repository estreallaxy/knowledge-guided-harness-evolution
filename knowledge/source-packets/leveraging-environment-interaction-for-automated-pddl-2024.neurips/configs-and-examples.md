# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `requirements.txt`
- `src/domains.py`
- `src/main.py`
- `src/problem_domain_translation.py`

## Upstream command excerpts

```text
pip install requirements.txt
```

```text
bash reproduce.sh
```

```text
📦domain
 ├ 📜domain.pddl               # The domain PDDL file
 ├ 📜domain_template.pddl      # Domain template PDDL
 ├ 📜domain.nl                 # Natural language description of the domain (GPT-generated).
 ├ 📜predicate_descriptor.py   # Mapping between NL descriptions and predicates (GPT-generated).
 ├ 📜p{i}.pddl                 # The {i}-th problem PDDL file
 ├ 📜p{i}_template.pddl        # The {i}-th problem template 
 ├ 📜p{i}.nl                   # Natural language description of the {i}-th problem (GPT-generated).
 ├ 📜p_example.pddl            # Example problem PDDL file.
 ├ 📜p_example_template.pddl   # Example problem template.
 ├ 📜p_example.nl              # Example natural language description.
 └ 📜p_example.sol             # Example solution.
```

```text
📦src
 ├ 📜back_translate.py         # Backtranslation utils for domain/problem/description natural language geneation
 ├ 📜domains.py              
 ├ 📜error_messages.py        
 ├ 📜evaluation.py            
 ├ 📜gen_pddl_template_pddl.py # Generates PDDL templates from the original PDDL files.
 ├ 📜gpt_client.py            
 ├ 📜intrinsic_planning.py     # Intrinsic planning baselines
 ├ 📜main.py                   # Main entry point for our method
 ├ 📜pddl_utils.py             # Utility functions to work with PDDL files.
 ├ 📜planning.py               # Core planning logic and functions.
 ├ 📜problem_domain_translation.py
 ├ 📜prompts.py               
 ├ 📂rw_analysis              # Analysis for exploration walk
 │  ├ 📜rw_analysis.py        # Core reward analysis logic.
 │  └ 📜rw_corr_plot.py       # Plots for reward correlation analysis.
 └ 📜utils.py
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
