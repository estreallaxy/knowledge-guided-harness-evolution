# StateFork 论文与代码定位

固定论文 `2609.38648v1`：§2.2 状态边界；§3.1–3.3 / PDF pp.6–7；§4 Waypoint；§5.2 / pp.11–12；附录 A 评测条件。

论文原样 PDF 见 [固定论文](paper/paper-v1.pdf)，全文文本按 PDF 页码分隔。代码保存范围是选定原样文件，不是完整可安装 checkout；与论文原实验 commit 的对应关系未知。

## Alex-XJK/StateFork

固定 revision：`9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c`；许可证：Apache-2.0。

| 固定代码位置 | 原始来源 | SHA256 |
| --- | --- | --- |
| [README.md](official-code/StateFork/README.md) | [上游固定文件](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/README.md) | `18aa6e9a22df6fc5bd3bfa39c787971cf08417911d03a385340341dbbb3b4e0e` |
| [LICENSE](official-code/StateFork/LICENSE) | [上游固定文件](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/LICENSE) | `cddf00b77e2d22068bde8e501d95bca1e3de615e0b4e905298e5752b04deea11` |
| [decider/decider.py](official-code/StateFork/decider/decider.py) | [上游固定文件](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/decider/decider.py) | `e553563e9d3f68b9e2d529fad4eacb142469f91c8c5404100256cb173919371a` |
| [controller/base_env_manager.py](official-code/StateFork/controller/base_env_manager.py) | [上游固定文件](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py) | `a7bbe9e8ccc31ed52ca3e926078171f8c15fc172ba1a1408ecddff2bbe25dfb3` |
| [controller/forkable_env_manager.py](official-code/StateFork/controller/forkable_env_manager.py) | [上游固定文件](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/forkable_env_manager.py) | `adfb91ae7270ebc5a8a12735749f4a2d2824b53a583899ce67d89c7f5fa26b2c` |
| [controller/waypoint_env_manager.py](official-code/StateFork/controller/waypoint_env_manager.py) | [上游固定文件](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/waypoint_env_manager.py) | `0082997942c9f9a2227767a68b7bf5c9c3c463120fc6b92b3aa8d3cad3f487b9` |

## Alex-XJK/waypoint

固定 revision：`dcb6a7b0f4114f4732b9d7f1d1824dc5e4ff4a24`；许可证：Apache-2.0。

| 固定代码位置 | 原始来源 | SHA256 |
| --- | --- | --- |
| [README.md](official-code/waypoint/README.md) | [上游固定文件](https://github.com/Alex-XJK/waypoint/blob/dcb6a7b0f4114f4732b9d7f1d1824dc5e4ff4a24/README.md) | `c7bfd71b2ac70bd8acd4d707461013f0fa6daf9def98a8b8855790aa8b408188` |
| [LICENSE](official-code/waypoint/LICENSE) | [上游固定文件](https://github.com/Alex-XJK/waypoint/blob/dcb6a7b0f4114f4732b9d7f1d1824dc5e4ff4a24/LICENSE) | `cddf00b77e2d22068bde8e501d95bca1e3de615e0b4e905298e5752b04deea11` |
| [pkg/waypoint/checkpoint.go](official-code/waypoint/pkg/waypoint/checkpoint.go) | [上游固定文件](https://github.com/Alex-XJK/waypoint/blob/dcb6a7b0f4114f4732b9d7f1d1824dc5e4ff4a24/pkg/waypoint/checkpoint.go) | `03cecc6fab5aaafff9369dafccb53373beabb14f4dfa574d2a349061b8939a01` |
| [docs/INSTALL.md](official-code/waypoint/docs/INSTALL.md) | [上游固定文件](https://github.com/Alex-XJK/waypoint/blob/dcb6a7b0f4114f4732b9d7f1d1824dc5e4ff4a24/docs/INSTALL.md) | `288810a96645d941b1da4bcc0b1d7e93a437bcd6847a6916e35dc5e235385783` |
| [go.mod](official-code/waypoint/go.mod) | [上游固定文件](https://github.com/Alex-XJK/waypoint/blob/dcb6a7b0f4114f4732b9d7f1d1824dc5e4ff4a24/go.mod) | `96c01ebb7fba1b9bc243ba028af4aa55754425c0d1a24cebbdc28530e49dee64` |

## 固定代码符号行号

- `DecisionContext`：[official-code/StateFork/decider/decider.py:6](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/decider/decider.py#L6)。
- `Decider`：[official-code/StateFork/decider/decider.py:10](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/decider/decider.py#L10)。
- `RandomDecider`：[official-code/StateFork/decider/decider.py:25](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/decider/decider.py#L25)。
- `AlwaysTrueDecider`：[official-code/StateFork/decider/decider.py:33](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/decider/decider.py#L33)。
- `AlwaysFalseDecider`：[official-code/StateFork/decider/decider.py:41](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/decider/decider.py#L41)。
- `ThresholdDecider`：[official-code/StateFork/decider/decider.py:49](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/decider/decider.py#L49)。
- `decide`：[official-code/StateFork/decider/decider.py:17](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/decider/decider.py#L17)。
- `decide`：[official-code/StateFork/decider/decider.py:30](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/decider/decider.py#L30)。
- `decide`：[official-code/StateFork/decider/decider.py:38](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/decider/decider.py#L38)。
- `decide`：[official-code/StateFork/decider/decider.py:46](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/decider/decider.py#L46)。
- `__init__`：[official-code/StateFork/decider/decider.py:52](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/decider/decider.py#L52)。
- `decide`：[official-code/StateFork/decider/decider.py:55](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/decider/decider.py#L55)。
- `SnapshotNode`：[official-code/StateFork/controller/base_env_manager.py:23](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L23)。
- `BranchState`：[official-code/StateFork/controller/base_env_manager.py:35](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L35)。
- `EnvironmentManager`：[official-code/StateFork/controller/base_env_manager.py:51](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L51)。
- `__init__`：[official-code/StateFork/controller/base_env_manager.py:64](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L64)。
- `__del__`：[official-code/StateFork/controller/base_env_manager.py:84](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L84)。
- `_get_current_branch_id`：[official-code/StateFork/controller/base_env_manager.py:94](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L94)。
- `_get_branch_state`：[official-code/StateFork/controller/base_env_manager.py:98](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L98)。
- `_register_branch`：[official-code/StateFork/controller/base_env_manager.py:106](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L106)。
- `_remove_branch`：[official-code/StateFork/controller/base_env_manager.py:122](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L122)。
- `_set_current_branch`：[official-code/StateFork/controller/base_env_manager.py:129](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L129)。
- `_set_branch_position`：[official-code/StateFork/controller/base_env_manager.py:136](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L136)。
- `current_snapshot_id`：[official-code/StateFork/controller/base_env_manager.py:152](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L152)。
- `current_snapshot_id`：[official-code/StateFork/controller/base_env_manager.py:157](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L157)。
- `last_snapshot_id`：[official-code/StateFork/controller/base_env_manager.py:162](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L162)。
- `last_snapshot_id`：[official-code/StateFork/controller/base_env_manager.py:167](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L167)。
- `_command_log`：[official-code/StateFork/controller/base_env_manager.py:172](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L172)。
- `_command_log`：[official-code/StateFork/controller/base_env_manager.py:177](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L177)。
- `_cumulative_exec_time`：[official-code/StateFork/controller/base_env_manager.py:182](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L182)。
- `_cumulative_exec_time`：[official-code/StateFork/controller/base_env_manager.py:187](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L187)。
- `_register_snapshot_resource`：[official-code/StateFork/controller/base_env_manager.py:195](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L195)。
- `_snapshot_resource`：[official-code/StateFork/controller/base_env_manager.py:199](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L199)。
- `_snapshot_items`：[official-code/StateFork/controller/base_env_manager.py:203](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L203)。
- `_remove_snapshot_resource`：[official-code/StateFork/controller/base_env_manager.py:207](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L207)。
- `_record_snapshot_node`：[official-code/StateFork/controller/base_env_manager.py:211](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L211)。
- `snapshot`：[official-code/StateFork/controller/base_env_manager.py:223](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L223)。
- `_snapshot_branch`：[official-code/StateFork/controller/base_env_manager.py:228](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L228)。
- `_after_snapshot`：[official-code/StateFork/controller/base_env_manager.py:293](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L293)。
- `_core_snapshot`：[official-code/StateFork/controller/base_env_manager.py:297](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L297)。
- `restore`：[official-code/StateFork/controller/base_env_manager.py:317](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L317)。
- `_restore_current_branch`：[official-code/StateFork/controller/base_env_manager.py:322](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L322)。
- `_core_restore`：[official-code/StateFork/controller/base_env_manager.py:384](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L384)。
- `cleanup`：[official-code/StateFork/controller/base_env_manager.py:409](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L409)。
- `_core_cleanup`：[official-code/StateFork/controller/base_env_manager.py:419](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L419)。
- `exec_command`：[official-code/StateFork/controller/base_env_manager.py:432](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L432)。
- `_exec_branch`：[official-code/StateFork/controller/base_env_manager.py:445](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L445)。
- `_core_exec`：[official-code/StateFork/controller/base_env_manager.py:496](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L496)。
- `copy_in`：[official-code/StateFork/controller/base_env_manager.py:509](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L509)。
- `copy_out`：[official-code/StateFork/controller/base_env_manager.py:526](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L526)。
- `_copy_branch`：[official-code/StateFork/controller/base_env_manager.py:536](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L536)。
- `_core_copy`：[official-code/StateFork/controller/base_env_manager.py:587](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L587)。
- `list_snapshots`：[official-code/StateFork/controller/base_env_manager.py:604](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L604)。
- `print_snapshot_tree`：[official-code/StateFork/controller/base_env_manager.py:608](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L608)。
- `current_snapshot`：[official-code/StateFork/controller/base_env_manager.py:650](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L650)。
- `backend`：[official-code/StateFork/controller/base_env_manager.py:654](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L654)。
- `stats`：[official-code/StateFork/controller/base_env_manager.py:658](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L658)。
- `recurse`：[official-code/StateFork/controller/base_env_manager.py:627](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/base_env_manager.py#L627)。
- `EnvironmentBranch`：[official-code/StateFork/controller/forkable_env_manager.py:23](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/forkable_env_manager.py#L23)。
- `ForkableEnvironmentManager`：[official-code/StateFork/controller/forkable_env_manager.py:34](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/forkable_env_manager.py#L34)。
- `__init__`：[official-code/StateFork/controller/forkable_env_manager.py:42](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/forkable_env_manager.py#L42)。
- `_validate_decider`：[official-code/StateFork/controller/forkable_env_manager.py:56](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/forkable_env_manager.py#L56)。
- `current_branch_id`：[official-code/StateFork/controller/forkable_env_manager.py:65](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/forkable_env_manager.py#L65)。
- `current_fork_id`：[official-code/StateFork/controller/forkable_env_manager.py:70](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/forkable_env_manager.py#L70)。
- `live_branches`：[official-code/StateFork/controller/forkable_env_manager.py:75](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/forkable_env_manager.py#L75)。
- `live_forks`：[official-code/StateFork/controller/forkable_env_manager.py:80](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/forkable_env_manager.py#L80)。
- `snapshot_branch`：[official-code/StateFork/controller/forkable_env_manager.py:84](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/forkable_env_manager.py#L84)。
- `exec_on_branch`：[official-code/StateFork/controller/forkable_env_manager.py:103](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/forkable_env_manager.py#L103)。
- `copy_in_branch`：[official-code/StateFork/controller/forkable_env_manager.py:118](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/forkable_env_manager.py#L118)。
- `copy_out_branch`：[official-code/StateFork/controller/forkable_env_manager.py:130](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/forkable_env_manager.py#L130)。
- `fork`：[official-code/StateFork/controller/forkable_env_manager.py:142](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/forkable_env_manager.py#L142)。
- `_fork`：[official-code/StateFork/controller/forkable_env_manager.py:152](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/forkable_env_manager.py#L152)。
- `_materialize_branches`：[official-code/StateFork/controller/forkable_env_manager.py:199](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/forkable_env_manager.py#L199)。
- `_core_fork`：[official-code/StateFork/controller/forkable_env_manager.py:225](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/forkable_env_manager.py#L225)。
- `_core_restore`：[official-code/StateFork/controller/forkable_env_manager.py:247](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/forkable_env_manager.py#L247)。
- `discard_branch`：[official-code/StateFork/controller/forkable_env_manager.py:277](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/forkable_env_manager.py#L277)。
- `_discard_branch`：[official-code/StateFork/controller/forkable_env_manager.py:282](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/forkable_env_manager.py#L282)。
- `destroy_fork`：[official-code/StateFork/controller/forkable_env_manager.py:313](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/forkable_env_manager.py#L313)。
- `_core_discard_branch`：[official-code/StateFork/controller/forkable_env_manager.py:318](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/forkable_env_manager.py#L318)。
- `park_branch`：[official-code/StateFork/controller/forkable_env_manager.py:332](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/forkable_env_manager.py#L332)。
- `_park_branch`：[official-code/StateFork/controller/forkable_env_manager.py:337](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/forkable_env_manager.py#L337)。
- `_core_park_branch`：[official-code/StateFork/controller/forkable_env_manager.py:386](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/forkable_env_manager.py#L386)。
- `list_branches`：[official-code/StateFork/controller/forkable_env_manager.py:401](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/forkable_env_manager.py#L401)。
- `_list_branches`：[official-code/StateFork/controller/forkable_env_manager.py:406](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/forkable_env_manager.py#L406)。
- `list_forks`：[official-code/StateFork/controller/forkable_env_manager.py:431](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/forkable_env_manager.py#L431)。
- `_core_list_branches`：[official-code/StateFork/controller/forkable_env_manager.py:436](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/forkable_env_manager.py#L436)。
- `_after_snapshot`：[official-code/StateFork/controller/forkable_env_manager.py:448](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/forkable_env_manager.py#L448)。
- `_resolve_bin`：[official-code/StateFork/controller/waypoint_env_manager.py:24](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/waypoint_env_manager.py#L24)。
- `_run_waypoint`：[official-code/StateFork/controller/waypoint_env_manager.py:50](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/waypoint_env_manager.py#L50)。
- `_assert_supports_forking`：[official-code/StateFork/controller/waypoint_env_manager.py:76](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/waypoint_env_manager.py#L76)。
- `_cpe_detail`：[official-code/StateFork/controller/waypoint_env_manager.py:114](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/waypoint_env_manager.py#L114)。
- `WaypointFork`：[official-code/StateFork/controller/waypoint_env_manager.py:121](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/waypoint_env_manager.py#L121)。
- `WaypointCalculator`：[official-code/StateFork/controller/waypoint_env_manager.py:165](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/waypoint_env_manager.py#L165)。
- `WaypointAttachManager`：[official-code/StateFork/controller/waypoint_env_manager.py:223](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/waypoint_env_manager.py#L223)。
- `WaypointBuildManager`：[official-code/StateFork/controller/waypoint_env_manager.py:631](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/waypoint_env_manager.py#L631)。
- `__init__`：[official-code/StateFork/controller/waypoint_env_manager.py:131](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/waypoint_env_manager.py#L131)。
- `base_checkpoint`：[official-code/StateFork/controller/waypoint_env_manager.py:156](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/waypoint_env_manager.py#L156)。
- `base_checkpoint`：[official-code/StateFork/controller/waypoint_env_manager.py:161](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/waypoint_env_manager.py#L161)。
- `__init__`：[official-code/StateFork/controller/waypoint_env_manager.py:178](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/waypoint_env_manager.py#L178)。
- `__get_all_items`：[official-code/StateFork/controller/waypoint_env_manager.py:184](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/waypoint_env_manager.py#L184)。
- `__get_size`：[official-code/StateFork/controller/waypoint_env_manager.py:196](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/waypoint_env_manager.py#L196)。
- `_collect`：[official-code/StateFork/controller/waypoint_env_manager.py:209](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/waypoint_env_manager.py#L209)。
- `__init__`：[official-code/StateFork/controller/waypoint_env_manager.py:244](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/waypoint_env_manager.py#L244)。
- `_snapshot_waypoint`：[official-code/StateFork/controller/waypoint_env_manager.py:301](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/waypoint_env_manager.py#L301)。
- `_core_snapshot`：[official-code/StateFork/controller/waypoint_env_manager.py:330](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/waypoint_env_manager.py#L330)。
- `_core_park_branch`：[official-code/StateFork/controller/waypoint_env_manager.py:338](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/waypoint_env_manager.py#L338)。
- `_core_cleanup`：[official-code/StateFork/controller/waypoint_env_manager.py:341](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/waypoint_env_manager.py#L341)。
- `_core_exec`：[official-code/StateFork/controller/waypoint_env_manager.py:362](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/waypoint_env_manager.py#L362)。
- `_core_fork`：[official-code/StateFork/controller/waypoint_env_manager.py:370](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/waypoint_env_manager.py#L370)。
- `_exec_raw`：[official-code/StateFork/controller/waypoint_env_manager.py:415](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/waypoint_env_manager.py#L415)。
- `_core_copy`：[official-code/StateFork/controller/waypoint_env_manager.py:442](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/waypoint_env_manager.py#L442)。
- `_core_discard_branch`：[official-code/StateFork/controller/waypoint_env_manager.py:486](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/waypoint_env_manager.py#L486)。
- `sync_snapshot_tree`：[official-code/StateFork/controller/waypoint_env_manager.py:503](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/waypoint_env_manager.py#L503)。
- `_core_list_branches`：[official-code/StateFork/controller/waypoint_env_manager.py:563](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/waypoint_env_manager.py#L563)。
- `_parse_fork_line`：[official-code/StateFork/controller/waypoint_env_manager.py:607](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/waypoint_env_manager.py#L607)。
- `__init__`：[official-code/StateFork/controller/waypoint_env_manager.py:635](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/waypoint_env_manager.py#L635)。
- `work_dir`：[official-code/StateFork/controller/waypoint_env_manager.py:693](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/waypoint_env_manager.py#L693)。
- `materialize`：[official-code/StateFork/controller/waypoint_env_manager.py:382](https://github.com/Alex-XJK/StateFork/blob/9fdb3242e5555f9edfc62d086e0b2e76a90b0a1c/controller/waypoint_env_manager.py#L382)。
