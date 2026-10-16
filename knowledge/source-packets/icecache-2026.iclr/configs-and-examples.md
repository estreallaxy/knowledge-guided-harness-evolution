# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/IceCache/3rdparty/flashinfer/3rdparty/googletest/googletest/test/googletest-global-environment-unittest.py` | Dependency, configuration, or usage evidence. |
| `official-code/IceCache/3rdparty/flashinfer/3rdparty/googletest/googletest/test/googletest-global-environment-unittest_.cc` | Dependency, configuration, or usage evidence. |
| `official-code/IceCache/3rdparty/flashinfer/3rdparty/googletest/googletest/test/googletest-setuptestsuite-test.py` | Dependency, configuration, or usage evidence. |
| `official-code/IceCache/3rdparty/flashinfer/3rdparty/googletest/googletest/test/gtest_environment_test.cc` | Dependency, configuration, or usage evidence. |
| `official-code/IceCache/3rdparty/flashinfer/3rdparty/googletest/googletest/test/gtest_skip_environment_check_output_test.py` | Dependency, configuration, or usage evidence. |
| `official-code/IceCache/3rdparty/flashinfer/3rdparty/googletest/googletest/test/gtest_skip_in_environment_setup_test.cc` | Dependency, configuration, or usage evidence. |
| `official-code/IceCache/benchmark/longbench_config/dataset2maxlen.json` | Dependency, configuration, or usage evidence. |
| `official-code/IceCache/benchmark/longbench_config/dataset2prompt.json` | Dependency, configuration, or usage evidence. |
| `official-code/IceCache/benchmark/longbench_config/model2maxlen.json` | Dependency, configuration, or usage evidence. |
| `official-code/IceCache/benchmark/longbench_config/model2path.json` | Dependency, configuration, or usage evidence. |
| `official-code/IceCache/source/setup.py` | Dependency, configuration, or usage evidence. |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/IceCache/3rdparty/flashinfer/3rdparty/googletest/googletest/test/gtest_skip_in_environment_setup_test.cc` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/IceCache/benchmark/longbench_metrics.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/IceCache/3rdparty/flashinfer/3rdparty/googletest/googletest/test/gtest_skip_environment_check_output_test.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/IceCache/3rdparty/flashinfer/3rdparty/googletest/googletest/test/googletest-global-environment-unittest.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/IceCache/3rdparty/flashinfer/3rdparty/googletest/googletest/test/googletest-global-environment-unittest_.cc` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/IceCache/3rdparty/flashinfer/3rdparty/googletest/googletest/test/gtest_environment_test.cc` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/IceCache/benchmark/longbench_eval.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/IceCache/source/icecache_cpp/src/gen_dispatch.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/IceCache/3rdparty/flashinfer/3rdparty/googletest/googletest/test/googletest-setuptestsuite-test.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/IceCache/3rdparty/flashinfer/3rdparty/googletest/googlemock/src/gmock-cardinalities.cc` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/IceCache/3rdparty/flashinfer/3rdparty/googletest/googlemock/src/gmock-internal-utils.cc` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/IceCache/source/icecache/infer_state.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
