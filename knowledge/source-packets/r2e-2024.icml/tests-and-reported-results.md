# Tests and reported results

## Official verification entry points

- `src/r2e/evaluators/testgen.py`
- `tests/generators/context/test_full.py`
- `tests/generators/context/test_naive.py`
- `tests/generators/context/test_sliced.py`
- `tests/pat/callgraph/test_cg_gen.py`
- `tests/pat/callgraph/test_cg_query.py`
- `tests/pat/slicers/test_slicer_main.py`
- `src/r2e/generators/testgen/prompt.py`
- `unittest.cfg`
- `tests/test_logger.py`
- `tests/models/test_models.py`
- `tests/repo_builder/test_extract_repo_data.py`
- `src/r2e/models/tests.py`
- `tests/pat/imports/test_resolver.py`
- `tests/pat/imports/test_transfomer.py`
- `src/r2e/generators/testgen/__init__.py`
- `src/r2e/generators/testgen/args.py`
- `src/r2e/generators/testgen/generate.py`
- `src/r2e/generators/testgen/genexec.py`
- `src/r2e/generators/testgen/oversample.py`
- `src/r2e/generators/testgen/task.py`
- `src/r2e/generators/testgen/utils.py`
- `tests/pat/slicers/test_globals_finder/__init__.py`
- `tests/pat/slicers/test_globals_finder/test_bytecode_globals.py`
- `tests/pat/slicers/test_globals_finder/test_defaultarg_globals.py`
- `tests/pat/slicers/test_globals_finder/test_expr_globals.py`
- `tests/pat/slicers/test_globals_finder/test_globals_finder.py`
- `tests/pat/slicers/test_globals_finder/test_stmt_globals.py`
- `tests/pat/slicers/test_globals_finder/test_type_ann_globals.py`

## Published result anchors

- p. 5: Table 2. Comparing R2E-Eval1 with other NL-to-code generation
- p. 6: Table 3. Statistics for problems instances in our R2E-Eval1. mentations (networkx, statistics), domain-specific problems
- p. 16: Table 4. Interface Understandability Scores Table 5. Problem Intent Scores
- p. 18: Table 6. List of models
- p. 29: Table 7. Effect of COT on code generation on a subset of our R2E-Eval1 benchmark

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | ICML 2024 |
| Official open-source implementation | https://github.com/r2e-project/r2e at `bcbed156711bb939de14aa46b27eee15073f5272` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
