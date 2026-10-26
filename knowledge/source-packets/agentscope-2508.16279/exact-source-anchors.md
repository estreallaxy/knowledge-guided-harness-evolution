# AgentScope 1.0 paper and code positioning

For the mechanism interface, usage boundaries and method relationships, see [Mechanism Description](mechanism-and-boundaries.md). For the paper page number, text line number and fixed code range of each claim, see [Evidence Map](claim-evidence-map.json).

Fixed paper`2508.16279v1`: §3.1.4 / PDF pp.10–11; fixed _agent_base.py, _agent_meta.py from v1.0.0.

The original PDF of the paper can be found in [Fixed paper](paper/paper-v1.pdf), and the full text is separated by PDF page numbers. The code saving range is the selected original file, which is not a complete installable checkout; the corresponding relationship with the original experimental commit of the paper is unknown.

## agentscope-ai/agentscope

Fixed revision:`47042b888b90bca2672567a041f61fb665da0bc6`; License: Apache-2.0.

|Fixed code location|original source|
| --- | --- |
| [README.md](official-code/agentscope/README.md) |[Upstream Fixed File](https://github.com/agentscope-ai/agentscope/blob/47042b888b90bca2672567a041f61fb665da0bc6/README.md)|
| [LICENSE](official-code/agentscope/LICENSE) |[Upstream Fixed File](https://github.com/agentscope-ai/agentscope/blob/47042b888b90bca2672567a041f61fb665da0bc6/LICENSE)|
| [src/agentscope/agent/_agent_base.py](official-code/agentscope/src/agentscope/agent/_agent_base.py) |[Upstream Fixed File](https://github.com/agentscope-ai/agentscope/blob/47042b888b90bca2672567a041f61fb665da0bc6/src/agentscope/agent/_agent_base.py)|
| [src/agentscope/agent/_agent_meta.py](official-code/agentscope/src/agentscope/agent/_agent_meta.py) |[Upstream Fixed File](https://github.com/agentscope-ai/agentscope/blob/47042b888b90bca2672567a041f61fb665da0bc6/src/agentscope/agent/_agent_meta.py)|
| [src/agentscope/_utils/_common.py](official-code/agentscope/src/agentscope/_utils/_common.py) |[Upstream Fixed File](https://github.com/agentscope-ai/agentscope/blob/47042b888b90bca2672567a041f61fb665da0bc6/src/agentscope/_utils/_common.py)|

## Fixed code symbol line number

- `AgentBase`: [official-code/agentscope/src/agentscope/agent/_agent_base.py:17](https://github.com/agentscope-ai/agentscope/blob/47042b888b90bca2672567a041f61fb665da0bc6/src/agentscope/agent/_agent_base.py#L17).
- `__init__`: [official-code/agentscope/src/agentscope/agent/_agent_base.py:127](https://github.com/agentscope-ai/agentscope/blob/47042b888b90bca2672567a041f61fb665da0bc6/src/agentscope/agent/_agent_base.py#L127).
- `observe`: [official-code/agentscope/src/agentscope/agent/_agent_base.py:158](https://github.com/agentscope-ai/agentscope/blob/47042b888b90bca2672567a041f61fb665da0bc6/src/agentscope/agent/_agent_base.py#L158).
- `reply`: [official-code/agentscope/src/agentscope/agent/_agent_base.py:170](https://github.com/agentscope-ai/agentscope/blob/47042b888b90bca2672567a041f61fb665da0bc6/src/agentscope/agent/_agent_base.py#L170).
- `print`: [official-code/agentscope/src/agentscope/agent/_agent_base.py:178](https://github.com/agentscope-ai/agentscope/blob/47042b888b90bca2672567a041f61fb665da0bc6/src/agentscope/agent/_agent_base.py#L178).
- `__call__`: [official-code/agentscope/src/agentscope/agent/_agent_base.py:226](https://github.com/agentscope-ai/agentscope/blob/47042b888b90bca2672567a041f61fb665da0bc6/src/agentscope/agent/_agent_base.py#L226).
- `_broadcast_to_subscribers`: [official-code/agentscope/src/agentscope/agent/_agent_base.py:246](https://github.com/agentscope-ai/agentscope/blob/47042b888b90bca2672567a041f61fb665da0bc6/src/agentscope/agent/_agent_base.py#L246).
- `handle_interrupt`: [official-code/agentscope/src/agentscope/agent/_agent_base.py:254](https://github.com/agentscope-ai/agentscope/blob/47042b888b90bca2672567a041f61fb665da0bc6/src/agentscope/agent/_agent_base.py#L254).
- `interrupt`: [official-code/agentscope/src/agentscope/agent/_agent_base.py:266](https://github.com/agentscope-ai/agentscope/blob/47042b888b90bca2672567a041f61fb665da0bc6/src/agentscope/agent/_agent_base.py#L266).
- `register_instance_hook`: [official-code/agentscope/src/agentscope/agent/_agent_base.py:271](https://github.com/agentscope-ai/agentscope/blob/47042b888b90bca2672567a041f61fb665da0bc6/src/agentscope/agent/_agent_base.py#L271).
- `remove_instance_hook`: [official-code/agentscope/src/agentscope/agent/_agent_base.py:299](https://github.com/agentscope-ai/agentscope/blob/47042b888b90bca2672567a041f61fb665da0bc6/src/agentscope/agent/_agent_base.py#L299).
- `register_class_hook`: [official-code/agentscope/src/agentscope/agent/_agent_base.py:329](https://github.com/agentscope-ai/agentscope/blob/47042b888b90bca2672567a041f61fb665da0bc6/src/agentscope/agent/_agent_base.py#L329).
- `remove_class_hook`: [official-code/agentscope/src/agentscope/agent/_agent_base.py:357](https://github.com/agentscope-ai/agentscope/blob/47042b888b90bca2672567a041f61fb665da0bc6/src/agentscope/agent/_agent_base.py#L357).
- `clear_class_hooks`: [official-code/agentscope/src/agentscope/agent/_agent_base.py:386](https://github.com/agentscope-ai/agentscope/blob/47042b888b90bca2672567a041f61fb665da0bc6/src/agentscope/agent/_agent_base.py#L386).
- `clear_instance_hooks`: [official-code/agentscope/src/agentscope/agent/_agent_base.py:409](https://github.com/agentscope-ai/agentscope/blob/47042b888b90bca2672567a041f61fb665da0bc6/src/agentscope/agent/_agent_base.py#L409).
- `reset_subscribers`: [official-code/agentscope/src/agentscope/agent/_agent_base.py:439](https://github.com/agentscope-ai/agentscope/blob/47042b888b90bca2672567a041f61fb665da0bc6/src/agentscope/agent/_agent_base.py#L439).
- `disable_console_output`: [official-code/agentscope/src/agentscope/agent/_agent_base.py:449](https://github.com/agentscope-ai/agentscope/blob/47042b888b90bca2672567a041f61fb665da0bc6/src/agentscope/agent/_agent_base.py#L449).
- `_normalize_to_kwargs`: [official-code/agentscope/src/agentscope/agent/_agent_meta.py:21](https://github.com/agentscope-ai/agentscope/blob/47042b888b90bca2672567a041f61fb665da0bc6/src/agentscope/agent/_agent_meta.py#L21).
- `_wrap_with_hooks`: [official-code/agentscope/src/agentscope/agent/_agent_meta.py:55](https://github.com/agentscope-ai/agentscope/blob/47042b888b90bca2672567a041f61fb665da0bc6/src/agentscope/agent/_agent_meta.py#L55).
- `_AgentMeta`: [official-code/agentscope/src/agentscope/agent/_agent_meta.py:147](https://github.com/agentscope-ai/agentscope/blob/47042b888b90bca2672567a041f61fb665da0bc6/src/agentscope/agent/_agent_meta.py#L147).
- `_ReActAgentMeta`: [official-code/agentscope/src/agentscope/agent/_agent_meta.py:165](https://github.com/agentscope-ai/agentscope/blob/47042b888b90bca2672567a041f61fb665da0bc6/src/agentscope/agent/_agent_meta.py#L165).
- `async_wrapper`: [official-code/agentscope/src/agentscope/agent/_agent_meta.py:67](https://github.com/agentscope-ai/agentscope/blob/47042b888b90bca2672567a041f61fb665da0bc6/src/agentscope/agent/_agent_meta.py#L67).
- `__new__`: [official-code/agentscope/src/agentscope/agent/_agent_meta.py:151](https://github.com/agentscope-ai/agentscope/blob/47042b888b90bca2672567a041f61fb665da0bc6/src/agentscope/agent/_agent_meta.py#L151).
- `__new__`: [official-code/agentscope/src/agentscope/agent/_agent_meta.py:169](https://github.com/agentscope-ai/agentscope/blob/47042b888b90bca2672567a041f61fb665da0bc6/src/agentscope/agent/_agent_meta.py#L169).
- `_json_loads_with_repair`: [official-code/agentscope/src/agentscope/_utils/_common.py:26](https://github.com/agentscope-ai/agentscope/blob/47042b888b90bca2672567a041f61fb665da0bc6/src/agentscope/_utils/_common.py#L26).
- `_is_accessible_local_file`: [official-code/agentscope/src/agentscope/_utils/_common.py:47](https://github.com/agentscope-ai/agentscope/blob/47042b888b90bca2672567a041f61fb665da0bc6/src/agentscope/_utils/_common.py#L47).
- `_get_timestamp`: [official-code/agentscope/src/agentscope/_utils/_common.py:52](https://github.com/agentscope-ai/agentscope/blob/47042b888b90bca2672567a041f61fb665da0bc6/src/agentscope/_utils/_common.py#L52).
- `_is_async_func`: [official-code/agentscope/src/agentscope/_utils/_common.py:63](https://github.com/agentscope-ai/agentscope/blob/47042b888b90bca2672567a041f61fb665da0bc6/src/agentscope/_utils/_common.py#L63).
- `_execute_async_or_sync_func`: [official-code/agentscope/src/agentscope/_utils/_common.py:79](https://github.com/agentscope-ai/agentscope/blob/47042b888b90bca2672567a041f61fb665da0bc6/src/agentscope/_utils/_common.py#L79).
- `_get_bytes_from_web_url`: [official-code/agentscope/src/agentscope/_utils/_common.py:105](https://github.com/agentscope-ai/agentscope/blob/47042b888b90bca2672567a041f61fb665da0bc6/src/agentscope/_utils/_common.py#L105).
- `_save_base64_data`: [official-code/agentscope/src/agentscope/_utils/_common.py:138](https://github.com/agentscope-ai/agentscope/blob/47042b888b90bca2672567a041f61fb665da0bc6/src/agentscope/_utils/_common.py#L138).
- `_extract_json_schema_from_mcp_tool`: [official-code/agentscope/src/agentscope/_utils/_common.py:163](https://github.com/agentscope-ai/agentscope/blob/47042b888b90bca2672567a041f61fb665da0bc6/src/agentscope/_utils/_common.py#L163).
- `_remove_title_field`: [official-code/agentscope/src/agentscope/_utils/_common.py:186](https://github.com/agentscope-ai/agentscope/blob/47042b888b90bca2672567a041f61fb665da0bc6/src/agentscope/_utils/_common.py#L186).
