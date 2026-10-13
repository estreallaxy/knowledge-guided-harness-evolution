# Separating Logical Branches from Physical State Recovery

StateFork represents an agent's exploration tree with logical nodes and lets the backend decide whether each node uses a physical checkpoint or command replay. Waypoint supplies an execution-session backend; the logical interface does not remove its recovery boundaries or operational prerequisites.

| Field | Mechanism |
| --- | --- |
| Target bottleneck | Branch exploration repeatedly restores shared prefixes: pure replay is expensive, while file snapshots may omit process and service state. |
| Role | Environment branch control, checkpoint-materialization policy, and execution-session backend. |
| Inputs | Active session, command sequence, parent/child nodes, cumulative replay time, and backend and checkpoint cost estimates. |
| Trigger | Search requests `snapshot`, `restore`, or `cleanup`; each snapshot decision chooses a physical or virtual representation. |
| Required steps | Create a logical node; materialize a checkpoint or save replay commands according to policy; restore the nearest physical ancestor; replay the suffix for a virtual node; maintain node relations and active state. |
| State changes | The logical-node tree and command log are updated; physical checkpoints are added or removed; the active session switches branches. |
| Outputs | Stable node identifiers, a recoverable session, execution observations, and time and storage records. |
| Preconditions and limits | Replay must reconstruct the relevant observations, and external services are not restored automatically. Waypoint requires Linux/root, CRIU, OverlayFS, and related facilities. The local backend has not been validated, and runner or environment changes fall outside the OptimizerLLM's editable Harness boundary. |

## Mechanism-to-evidence mapping

| ID | Claim | Paper and pinned code | Supported scope |
| --- | --- | --- | --- |
| SF1 | A virtual node is restored from a physical ancestor plus a command suffix. | PDF p.6 §3.1–3.2; `controller/base_env_manager.py:_snapshot_branch`, `_restore_current_branch` | Supports the public logical layer. The code only logs nonzero exits during replay, so a successful return alone does not establish equivalent observations. |
| SF2 | The paper compares physical-checkpoint cost with replay cost; the pinned code uses a default five-second threshold. | PDF pp.6–7 §3.2; `decider/decider.py:ThresholdDecider` | Establishes a difference between the paper's estimator and the pinned implementation; the threshold implementation must not be described as reproducing the paper's linear cost model. |
| SF3 | Waypoint session recovery requires specific operating-system and backend capabilities. | PDF p.7 §4, p.12 §6; Waypoint `docs/INSTALL.md` | Supports the paper scope and pinned installation requirements; backend operability, isolation, and local cost remain unknown. |
| SF4 | The pinned forkable manager currently supports only physical snapshots. | `controller/forkable_env_manager.py:_validate_decider` | Public-code constraint; logical-layer virtual-node support must not be generalized to this concurrent-branch implementation. |

Exact locations appear in [the evidence map](claim-evidence-map.json). System-level benefits, Smart Decider cost results, and local adaptation differences are recorded in [the results boundary](tests-and-reported-results.md). The pinned code has not been verified as the exact commit used for the paper's experiments.

## Method relationships and project-use boundary

- [AgentRewind](../agentrewind-2608.14380/mechanism-and-boundaries.md): SF1/SF3 and AR2 expose different recovery boundaries. A logical control interface is useful, but file restoration cannot substitute for process or session restoration.
- [AgentScope](../agentscope-2508.16279/mechanism-and-boundaries.md): AS1 pre/post hooks could record SF1 branch actions and timing as an adaptation hypothesis. Hook registration does not provide a checkpoint backend or establish a gain from combining the methods.

This packet preserves logical/physical state separation as a design source. It does not deploy a backend or modify a shared runner. Rollback must retain cumulative consumption and must not silently count failed replay or missing external state as reliable recovery.
