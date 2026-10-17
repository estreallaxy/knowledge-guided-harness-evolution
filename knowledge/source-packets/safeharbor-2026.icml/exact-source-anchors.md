# Exact source anchors

## Selected mechanism

Retain context-aware defense-rule extraction, hierarchical local memory, dynamic rule injection, and entropy-driven node splitting and merging; the selected guardrail is training-free.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | framework |
| Experimental setup | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | 4. Experimental Setup |
| Results and ablations | PDF p.8; `paper/paper-icml2026.txt` marker `===== PDF p.8 =====` | analysis |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/Agent-SafetyBench/environments/MemoryMetricsAnalyzer.py:3` | `MemoryMetricsAnalyzer` | Pinned implementation entry for the selected mechanism. |
| `official-code/Agent-SafetyBench/environments/PersonalizedBiometricSecurity.py:3` | `PersonalizedBiometricSecurity` | Pinned implementation entry for the selected mechanism. |
| `official-code/Agent-SafetyBench/environments/BiometricSecuritySystem.py:4` | `BiometricSecuritySystem` | Pinned implementation entry for the selected mechanism. |
| `official-code/Agent-SafetyBench/environments/PersonalizedBiometricAuthenticationForFinancialTransactions.py:3` | `PersonalizedBiometricAuthenticationForFinancialTransactions` | Pinned implementation entry for the selected mechanism. |
| `official-code/Agent-SafetyBench/environments/PersonalizedBiometricHealthMonitoring.py:3` | `PersonalizedBiometricHealthMonitoring` | Pinned implementation entry for the selected mechanism. |
| `official-code/Agent-SafetyBench/environments/BiometricallySecuredDataVault.py:4` | `BiometricallySecuredDataVault` | Pinned implementation entry for the selected mechanism. |
| `official-code/Agent-SafetyBench/environments/PersonalizedBiometricAccessControl.py:3` | `PersonalizedBiometricAccessControl` | Pinned implementation entry for the selected mechanism. |
| `official-code/Agent-SafetyBench/environments/BiometricAuthentication.py:4` | `BiometricAuthentication` | Pinned implementation entry for the selected mechanism. |
| `official-code/Agent-SafetyBench/environments/BorderSecuritySystem.py:4` | `BorderSecuritySystem` | Pinned implementation entry for the selected mechanism. |
| `official-code/Agent-SafetyBench/environments/ResearchDatabase.py:4` | `ResearchDatabase` | Pinned implementation entry for the selected mechanism. |
| `official-code/Agent-SafetyBench/environments/VerticalFarmOrchestrator.py:4` | `VerticalFarmOrchestrator` | Pinned implementation entry for the selected mechanism. |
| `official-code/Agent-SafetyBench/environments/SecurityManager.py:3` | `SecurityManager` | Pinned implementation entry for the selected mechanism. |
| `official-code/Agent-SafetyBench/environments/RealEstateManagementSystem.py:3` | `RealEstateManagementSystem` | Pinned implementation entry for the selected mechanism. |
| `official-code/Agent-SafetyBench/environments/RealEstateAssistant.py:4` | `RealEstateAssistant` | Pinned implementation entry for the selected mechanism. |
| `official-code/Agent-SafetyBench/environments/EthicsResearchLab.py:4` | `EthicsResearchLab` | Pinned implementation entry for the selected mechanism. |
| `official-code/Agent-SafetyBench/environments/SmartGridCybersecurity.py:4` | `SmartGridCybersecurity` | Pinned implementation entry for the selected mechanism. |
| `official-code/Agent-SafetyBench/environments/QuantumCryptographyImplementation.py:3` | `QuantumCryptographyImplementation` | Pinned implementation entry for the selected mechanism. |
| `official-code/Agent-SafetyBench/environments/PersonalizedCybersecurityThreatAssessment.py:3` | `PersonalizedCybersecurityThreatAssessment` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `4aa2be3bce7117739950b0de8ad4a5cebd1f81d7`. Paper page numbers refer to the fixed local proceedings PDF.
