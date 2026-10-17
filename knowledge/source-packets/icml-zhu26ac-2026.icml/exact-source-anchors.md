# Exact source anchors

## Selected mechanism

Retain ALIGN's decentralized gossip exchange, reputation formation, trust evaluation, hierarchical tone control, and defector-ostracism mechanism.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.4; `paper/paper-icml2026.txt` marker `===== PDF p.4 =====` | framework |
| Experimental setup | PDF p.5; `paper/paper-icml2026.txt` marker `===== PDF p.5 =====` | 5. Experiments |
| Results and ablations | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/main.py:18` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/scenarios/pd/agent.py:5` | `BaselineAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/scenarios/pd/agent.py:81` | `GossipAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/scenarios/pd/agent.py:158` | `GreedyAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/scenarios/donor/agent.py:5` | `BaselineAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/scenarios/donor/agent.py:87` | `GossipAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/scenarios/donor/agent.py:169` | `GreedyAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/scenarios/market/agent.py:5` | `SellerBaselineAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/scenarios/market/agent.py:110` | `SellerGossipAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/scenarios/market/agent.py:166` | `BuyerBaselineAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/scenarios/donor/prompt.py:6` | `rulePrompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/scenarios/donor/prompt.py:93` | `donationPrompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/scenarios/donor/prompt.py:226` | `gossipPrompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/scenarios/pd/prompt.py:6` | `rulePrompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/scenarios/pd/prompt.py:94` | `actionPrompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/scenarios/pd/prompt.py:234` | `gossipPrompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/scenarios/market/prompt.py:5` | `rulePrompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/scenarios/market/prompt.py:78` | `sellerPrompt` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `7e858032b220c8fb523cbb2cbc94dc66bc918883`. Paper page numbers refer to the fixed local proceedings PDF.
