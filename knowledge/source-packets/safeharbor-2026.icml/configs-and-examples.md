# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/Agent-SafetyBench/environments/BiometricAuthentication.json` | Dependency, configuration, or usage evidence. |
| `official-code/Agent-SafetyBench/environments/BiometricAuthentication.py` | Dependency, configuration, or usage evidence. |
| `official-code/Agent-SafetyBench/environments/BiometricSecuritySystem.json` | Dependency, configuration, or usage evidence. |
| `official-code/Agent-SafetyBench/environments/BiometricSecuritySystem.py` | Dependency, configuration, or usage evidence. |
| `official-code/Agent-SafetyBench/environments/BiometricallySecuredDataVault.json` | Dependency, configuration, or usage evidence. |
| `official-code/Agent-SafetyBench/environments/BiometricallySecuredDataVault.py` | Dependency, configuration, or usage evidence. |
| `official-code/Agent-SafetyBench/environments/BorderSecuritySystem.py` | Dependency, configuration, or usage evidence. |
| `official-code/Agent-SafetyBench/environments/EthicsResearchLab.py` | Dependency, configuration, or usage evidence. |
| `official-code/Agent-SafetyBench/environments/MemoryMetricsAnalyzer.json` | Dependency, configuration, or usage evidence. |
| `official-code/Agent-SafetyBench/environments/MemoryMetricsAnalyzer.py` | Dependency, configuration, or usage evidence. |
| `official-code/Agent-SafetyBench/environments/PersonalizedBiometricAccessControl.json` | Dependency, configuration, or usage evidence. |
| `official-code/Agent-SafetyBench/environments/PersonalizedBiometricAccessControl.py` | Dependency, configuration, or usage evidence. |
| `official-code/Agent-SafetyBench/environments/PersonalizedBiometricAuthenticationForFinancialTransactions.json` | Dependency, configuration, or usage evidence. |
| `official-code/Agent-SafetyBench/environments/PersonalizedBiometricAuthenticationForFinancialTransactions.py` | Dependency, configuration, or usage evidence. |
| `official-code/Agent-SafetyBench/environments/PersonalizedBiometricHealthMonitoring.json` | Dependency, configuration, or usage evidence. |
| `official-code/Agent-SafetyBench/environments/PersonalizedBiometricHealthMonitoring.py` | Dependency, configuration, or usage evidence. |
| `official-code/Agent-SafetyBench/environments/PersonalizedBiometricSecurity.json` | Dependency, configuration, or usage evidence. |
| `official-code/Agent-SafetyBench/environments/PersonalizedBiometricSecurity.py` | Dependency, configuration, or usage evidence. |
| `official-code/Agent-SafetyBench/environments/PersonalizedCybersecurityThreatAssessment.py` | Dependency, configuration, or usage evidence. |
| `official-code/Agent-SafetyBench/environments/QuantumCryptographyImplementation.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/Agent-SafetyBench/score/eval.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/Agent-SafetyBench/score/eval_with_shield.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/Agent-SafetyBench/score/eval_with_shield.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/baselines/guardagent/main.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/baselines/guardagent/main_agentalign.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/baselines/guardagent/run_guardagent_agentalign.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/run_agentharm.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
