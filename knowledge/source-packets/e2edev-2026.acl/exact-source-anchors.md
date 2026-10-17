# Exact source anchors

## Selected mechanism

To address these limitations, we present E2EDev, a novel benchmark grounded in the principles of Behavior-Driven Development (BDD) to assess whether the generated software meets user needs through mimicking real user interactions.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-acl2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.9; `paper/paper-acl2026.txt` marker `===== PDF p.9 =====` | design |
| Experimental setup | PDF p.22; `paper/paper-acl2026.txt` marker `===== PDF p.22 =====` | Experimental Setup |
| Results and ablations | PDF p.1; `paper/paper-acl2026.txt` marker `===== PDF p.1 =====` | analysis |
| Limitations or failure conditions | PDF p.9; `paper/paper-acl2026.txt` marker `===== PDF p.9 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/run_behave_test.py:12` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/Metrics/effectiveness.py:4` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/Metrics/efficiency/ana_tokens_time_gpt_engineer_22.py:63` | `calculate_operational_carbon` | Pinned implementation entry for the selected mechanism. |
| `official-code/Metrics/efficiency/ana_tokens_time_gpt_engineer_22.py:73` | `calculate_carbon_footprint` | Pinned implementation entry for the selected mechanism. |
| `official-code/Metrics/efficiency/ana_tokens_time_gpt_engineer_22.py:82` | `calculate_cost` | Pinned implementation entry for the selected mechanism. |
| `official-code/Metrics/efficiency/ana_tokens_time_llm_based_22.py:63` | `calculate_operational_carbon` | Pinned implementation entry for the selected mechanism. |
| `official-code/Metrics/efficiency/ana_tokens_time_llm_based_22.py:73` | `calculate_carbon_footprint` | Pinned implementation entry for the selected mechanism. |
| `official-code/Metrics/efficiency/ana_tokens_time_llm_based_22.py:82` | `calculate_cost` | Pinned implementation entry for the selected mechanism. |
| `official-code/Metrics/efficiency/ana_tokens_time_mapcoder_22.py:63` | `calculate_operational_carbon` | Pinned implementation entry for the selected mechanism. |
| `official-code/Metrics/efficiency/ana_tokens_time_mapcoder_22.py:73` | `calculate_carbon_footprint` | Pinned implementation entry for the selected mechanism. |
| `official-code/Metrics/efficiency/ana_tokens_time_mapcoder_22.py:82` | `calculate_cost` | Pinned implementation entry for the selected mechanism. |
| `official-code/Metrics/efficiency/ana_tokens_time_chatdev_22.py:64` | `calculate_operational_carbon` | Pinned implementation entry for the selected mechanism. |
| `official-code/Metrics/efficiency/ana_tokens_time_chatdev_22.py:74` | `calculate_carbon_footprint` | Pinned implementation entry for the selected mechanism. |
| `official-code/Metrics/efficiency/ana_tokens_time_chatdev_22.py:83` | `calculate_cost` | Pinned implementation entry for the selected mechanism. |
| `official-code/Metrics/efficiency/ana_tokens_time_self_colla_22.py:64` | `calculate_operational_carbon` | Pinned implementation entry for the selected mechanism. |
| `official-code/Metrics/efficiency/ana_tokens_time_self_colla_22.py:74` | `calculate_carbon_footprint` | Pinned implementation entry for the selected mechanism. |
| `official-code/Metrics/efficiency/ana_tokens_time_self_colla_22.py:83` | `calculate_cost` | Pinned implementation entry for the selected mechanism. |
| `official-code/Metrics/efficiency/ana_tokens_time_metagpt_22.py:11` | `parse_time` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `d280dd144fbff30c237af26c1a76948e2f8857fa`. Paper page numbers refer to the fixed local proceedings PDF.
