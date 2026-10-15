# Exact source anchors

## Selected mechanism

Extract repository functions/methods, synthesize executable equivalence tests, containerize dependencies, and expose each repository as an interactive program environment.

## Paper anchors

- p. 3: evaluation of which our framework enables. but repositories in the wild can be quite noisy, hard to run,
- p. 3: framework that turns any G IT H UB repository into a test
- p. 9: framework and environments for interactive general-purpose convert G IT H UB repositories to programming agent test
- p. 9: approach and use them for performing function correctness
- p. 9: Limitations. Natural language is inherently ambiguous and
- p. 9: approach along with manual filtering. Future work study S. Codeplan: Repository-level coding using llms and
- p. 22: results = _compare_inchis(inchi_true, inchi_pred)
- p. 22: results[’inchi_crystal_valid’] = _is_valid_inchi(inchi_true)
- p. 22: results[’inchi_docked_valid’] = _is_valid_inchi(inchi_pred)
- p. 22: results[’inchi_crystal’] = inchi_true
- p. 22: results[’inchi_docked’] = inchi_pred

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
- `pyproject.toml`
- `src/r2e/pat/README.md`
- `src/r2e/repo_builder/README.md`
- `src/r2e/generators/specgen/README.md`
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
- `src/r2e/config.yml`
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

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. The selected artifact is environment construction and verification, not model training. The paper evaluates generated tasks/tests and the code exposes extraction, static analysis, spec refinement, execution, and tests.

## Symbol-level code anchors

- `src/r2e/evaluators/testgen.py:10` — `TestGenEvaluator`
- `tests/generators/context/test_full.py:15` — `TestFullContextCreator`
- `tests/generators/context/test_naive.py:14` — `TestNaiveContextCreator`
- `tests/generators/context/test_sliced.py:14` — `TestSlicedContextCreator`
- `tests/pat/callgraph/test_cg_gen.py:8` — `TestCallGraphGenerator`
- `tests/pat/callgraph/test_cg_query.py:42` — `TestCallGraphExplorer`
- `tests/pat/slicers/test_slicer_main.py:21` — `get_slice`
- `tests/test_logger.py:8` — `TestLogger`
- `tests/models/test_models.py:52` — `TestRepo`
- `tests/repo_builder/test_extract_repo_data.py:7` — `TestExtractRepoData`
- `src/r2e/models/tests.py:5` — `Tests`
- `tests/pat/imports/test_resolver.py:10` — `TestImportResolver`
