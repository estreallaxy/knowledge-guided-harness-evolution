# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/Agent_SafetyBench/environments/BiometricAuthentication.json` | Dependency, configuration, or usage evidence. |
| `official-code/Agent_SafetyBench/environments/BiometricAuthentication.py` | Dependency, configuration, or usage evidence. |
| `official-code/Agent_SafetyBench/environments/BiometricSecuritySystem.json` | Dependency, configuration, or usage evidence. |
| `official-code/Agent_SafetyBench/environments/BiometricSecuritySystem.py` | Dependency, configuration, or usage evidence. |
| `official-code/Agent_SafetyBench/environments/BiometricallySecuredDataVault.json` | Dependency, configuration, or usage evidence. |
| `official-code/Agent_SafetyBench/environments/BiometricallySecuredDataVault.py` | Dependency, configuration, or usage evidence. |
| `official-code/Agent_SafetyBench/environments/BorderSecuritySystem.py` | Dependency, configuration, or usage evidence. |
| `official-code/Agent_SafetyBench/environments/MemoryMetricsAnalyzer.json` | Dependency, configuration, or usage evidence. |
| `official-code/Agent_SafetyBench/environments/MemoryMetricsAnalyzer.py` | Dependency, configuration, or usage evidence. |
| `official-code/Agent_SafetyBench/environments/PersonalizedBiometricAccessControl.json` | Dependency, configuration, or usage evidence. |
| `official-code/Agent_SafetyBench/environments/PersonalizedBiometricAccessControl.py` | Dependency, configuration, or usage evidence. |
| `official-code/Agent_SafetyBench/environments/PersonalizedBiometricAuthenticationForFinancialTransactions.json` | Dependency, configuration, or usage evidence. |
| `official-code/Agent_SafetyBench/environments/PersonalizedBiometricAuthenticationForFinancialTransactions.py` | Dependency, configuration, or usage evidence. |
| `official-code/Agent_SafetyBench/environments/PersonalizedBiometricHealthMonitoring.json` | Dependency, configuration, or usage evidence. |
| `official-code/Agent_SafetyBench/environments/PersonalizedBiometricHealthMonitoring.py` | Dependency, configuration, or usage evidence. |
| `official-code/Agent_SafetyBench/environments/PersonalizedBiometricSecurity.json` | Dependency, configuration, or usage evidence. |
| `official-code/Agent_SafetyBench/environments/PersonalizedBiometricSecurity.py` | Dependency, configuration, or usage evidence. |
| `official-code/Agent_SafetyBench/environments/ResearchDatabase.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/STAC_eval/eval_STAC_benchmark.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
