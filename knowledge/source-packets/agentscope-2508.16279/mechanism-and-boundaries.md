# Input and output contract of instance and class life cycle callback

AgentScope's lifecycle hooks allow extending behavior without directly modifying core methods. Fixed v1.0.0 implementation defining callback ordering, argument copying, and return value update semantics; these interface facts do not equate to performance gains for hook components.

|Field|Mechanism description|
| --- | --- |
|target bottleneck|Log, checksum and behavior extensions directly invade the agent core code and are difficult to combine independently.|
|function module|Lifecycle extension registration and asynchronous method packaging|
|enter|Hook type and name, callback function, method parameters, original method output|
|Trigger condition|Before the wrapped method is executed/after returning normally; the callback must be registered|
|Necessary steps|Register instance or class callback; normalize parameters; execute pre in sequence; call the original method; execute post in sequence; return update output|
|status change|Callback registry additions and deletions; pre can replace parameters, post can replace results, None means no replacement|
|expected output|Output according to the updated method of the callback contract, and expand self-saved records|
|Prerequisites and limitations|The return value of pre must satisfy the parameter dictionary contract; the compatibility of parameters and output deepcopy and the callback overhead are unknown. If the original method is abnormal, it will not enter the normal post, and the post cannot be used as a must-clean or crash recovery guarantee.|

## Correspondence between mechanism and evidence

|logo|advocate|Papers and Fixed Code|Support scope|
| --- | --- | --- | --- |
| AS1 |Life cycle pre/post hook can modify input and output| PDF pp.10–11 §3.1.4; `_agent_meta.py:_wrap_with_hooks` |Supports paper interface design and fixed packaging implementation, but does not support independent income conclusions|
| AS2 |Instance callbacks precede class callbacks. Parameters and results are copied and passed in. None is not replaced.| `_agent_meta.py:_wrap_with_hooks` |The specific semantics of the fixed code; the paper does not specify the order and copying contract|
| AS3 |Registering a hook with the same name will overwrite the original callback; the original method exception will not trigger the normal post| `_agent_base.py:register_instance_hook`, `register_class_hook`; `_agent_meta.py:_wrap_with_hooks` |Fixed code behavior; no analogy to finally hooks or exception recovery capabilities|

See [evidence map](claim-evidence-map.json) for the exact line number and range hash. The paper mentions events such as reasoning/acting, but this package selects`_agent_base.py`and`_agent_meta.py`to mainly check reply/observe/print; the unarchived parts will not be reworked to implement the location. For frame results and hook ablation boundaries, see [Result Description](tests-and-reported-results.md).

## Method relationships and project usage boundaries

- [NORA](../nora-2605.02092/mechanism-and-boundaries.md): AS1–AS3 are in-process function callbacks, NO1–NO2 are host command events and file handovers; trigger timing, input format, exception and exit code contracts are different and cannot be directly interchanged.
- [StateFork](../statefork-2609.38648/mechanism-and-boundaries.md): AS1 can be used to observe the action and consumption of SF1; this is the wiring under test and does not provide physical recovery capabilities.

The callback failure semantics, order and cost need to be independently verified for future access; currently, the complete framework has not been installed, H0 has not been connected, and the migration benefits have not been measured. It cannot be claimed that the overall framework benefits are brought by hooks just because the interface is verifiable.
