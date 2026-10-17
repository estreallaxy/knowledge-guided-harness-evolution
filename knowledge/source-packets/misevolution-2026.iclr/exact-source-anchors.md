# Exact source anchors

## Selected mechanism

Probe self-evolution runs for harmful or unintended behavioral drift with scenario-based risk metrics and trace analysis.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-iclr2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Results and ablations | PDF p.5; `paper/paper-iclr2026.txt` marker `===== PDF p.5 =====` | analysis |
| Limitations or failure conditions | PDF p.18; `paper/paper-iclr2026.txt` marker `===== PDF p.18 =====` | Limitation |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/model_misevolution/Agent-SafetyBench/environments/MemoryMetricsAnalyzer.py:3` | `MemoryMetricsAnalyzer` | Pinned implementation entry for the selected mechanism. |
| `official-code/model_misevolution/Agent-SafetyBench/environments/PersonalizedBiometricSecurity.py:3` | `PersonalizedBiometricSecurity` | Pinned implementation entry for the selected mechanism. |
| `official-code/model_misevolution/Agent-SafetyBench/environments/BiometricSecuritySystem.py:4` | `BiometricSecuritySystem` | Pinned implementation entry for the selected mechanism. |
| `official-code/model_misevolution/Agent-SafetyBench/environments/PersonalizedBiometricAuthenticationForFinancialTransactions.py:3` | `PersonalizedBiometricAuthenticationForFinancialTransactions` | Pinned implementation entry for the selected mechanism. |
| `official-code/model_misevolution/Agent-SafetyBench/environments/PersonalizedBiometricHealthMonitoring.py:3` | `PersonalizedBiometricHealthMonitoring` | Pinned implementation entry for the selected mechanism. |
| `official-code/model_misevolution/Agent-SafetyBench/environments/BiometricallySecuredDataVault.py:4` | `BiometricallySecuredDataVault` | Pinned implementation entry for the selected mechanism. |
| `official-code/model_misevolution/Agent-SafetyBench/environments/PersonalizedBiometricAccessControl.py:3` | `PersonalizedBiometricAccessControl` | Pinned implementation entry for the selected mechanism. |
| `official-code/model_misevolution/Agent-SafetyBench/environments/BiometricAuthentication.py:4` | `BiometricAuthentication` | Pinned implementation entry for the selected mechanism. |
| `official-code/model_misevolution/Agent-SafetyBench/environments/BorderSecuritySystem.py:4` | `BorderSecuritySystem` | Pinned implementation entry for the selected mechanism. |
| `official-code/model_misevolution/Agent-SafetyBench/environments/ResearchDatabase.py:4` | `ResearchDatabase` | Pinned implementation entry for the selected mechanism. |
| `official-code/model_misevolution/Agent-SafetyBench/score/eval_with_shield.py:30` | `create_model_tokenizer` | Pinned implementation entry for the selected mechanism. |
| `official-code/model_misevolution/Agent-SafetyBench/score/eval_with_shield.py:57` | `format_env_info` | Pinned implementation entry for the selected mechanism. |
| `official-code/model_misevolution/Agent-SafetyBench/score/eval_with_shield.py:85` | `format_input_dialog` | Pinned implementation entry for the selected mechanism. |
| `official-code/tool_misevolution/insecure_tool_creation/agent_workflow.py:13` | `MCPToolMatcher` | Pinned implementation entry for the selected mechanism. |
| `official-code/tool_misevolution/insecure_tool_creation/agent_workflow.py:112` | `AgentWorkflow` | Pinned implementation entry for the selected mechanism. |
| `official-code/tool_misevolution/insecure_tool_creation/agent_workflow.py:413` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/memory_misevolution/reward_hacking_test.py:320` | `RewardHackingTester` | Pinned implementation entry for the selected mechanism. |
| `official-code/memory_misevolution/reward_hacking_test.py:633` | `main` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `2601397de8b3de809d920555f05675d0a40a5979`. Paper page numbers refer to the fixed local proceedings PDF.
