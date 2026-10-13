# Exact source anchors

The page number is calculated as`paper/paper-v3.pdf`(57 pages, including appendices), which can be checked with the`--- PDF page N ---`mark of`paper/paper-v3.txt`.

## paper

|What to check|precise location|Range of original text support|
| --- | --- | --- |
|Two bottlenecks: unbounded growth brings inference memory cost + irrelevant information leads to inference degradation| Abstract, PDF p.1 |The paper ranks the two as key bottlenecks in long-range agentic tasks; no formal definition is given.|
|Unified compression of **Observation** and **History**| Abstract, PDF p.1; §3, PDF p.3 |ACON's framework positioning; "unification" is the point of difference compared to existing methods that only focus on one.|
|Optimizing compression guide in **natural language space**, no need to update the parameters of the model under test| Abstract, PDF p.1; §2, PDF p.2 |Model-agnostic can be applied directly; it cannot be inferred to be valid for all models.|
|Guide optimization based on agent's **failure analysis** iteration| Abstract, PDF p.1; §3.3, PDF p.5 |This is a key difference from static heuristic compression; the paper does not prove that failure attribution is always correct.|
|Distill the optimized compressor into a small model| §3.4, PDF p.5; Table 13, PDF p.25 |After distillation, student replaces teacher during reasoning.|
|Three claims: peak token reduction by 26–54%, success rate better than compression baseline, small model up to +46%| §1, PDF p.2; §3.2, PDF p.3 |"26–54%" is the range across benchmarks/settings; "+46%" is for the scenario where a small model is used as a long-range agent.|
|Evaluation objects: AppWorld, OfficeBench, 8-objective QA| §1, PDF p.2; §4, PDF p.6 |The difficulty stratification and indicator definitions of the three benchmarks are shown in Table 1/2.|
|Unify the agent skeleton into ReAct| §4, PDF p.6 |All experiments continued to use the ReAct style agent; the behavior after changing the agent was not reported.|
|Main results: Comparison of compression schemes in AppWorld| Table 1, PDF p.6 |The table notes indicate that each column is accuracy / steps / peak input tokens(10³) / dependency(10⁶).|
|Main results: OfficeBench vs. 8-objective QA| Table 2, PDF p.7 |Give acc/EM/F1and steps/peak/dependencyat the same time.|
|Ablation: optimizer models and task contrastive feedback| Table 3, PDF p.9 |Default o3 + contrastive feedback is optimal.|
|Actual efficiency: API cost and single question latency| Table 4, PDF p.9 |Cost estimated using gpt-4.1 agent + Qwen3-14B compressor; latency is mid-range on a single A100.|
|The effect of distillation| Table 13, PDF p.25 |The optimized guide still brings improvements on small models.|
|limit|Limitations after §5, PDF p.9; detailed discussion PDF p.16|It clearly acknowledges that there are still limitations and does not claim universality.|

## Official code

The line number anchor point is calculated according to the`official-code/`snapshot (revision`d63f9ae18959dc7215ff62899c94c5e8c56847ae`).

|mechanism or evidence|code location|effect|
| --- | --- | --- |
|Compressor base class| `src/productive_agents/ctxopt/base.py:17` (`BaseContextOptimizer`) |Common interface for observation/history compressors.|
|history compression| `src/productive_agents/ctxopt/history_optimizer.py:19` (`HistoryOptimizer`) |The main implementation of historical summary compression;`:135`determines whether re-summarization is needed.|
|Variants of history compression| `src/productive_agents/ctxopt/history_optimizer.py:216` (`HistoryOptimizerV2`), `src/productive_agents/ctxopt/history_optimizer.py:335` (`HistoryRetriever`) |Corresponds to the paper "Unified Compression" and the retrieval baseline.|
|Watch compression| `src/productive_agents/ctxopt/obs_optimizer.py:20` (`ObservationOptimizer`), `src/productive_agents/ctxopt/obs_optimizer.py:188` (`ObservationOptimizerV2`) |Observe the main compression implementation and variants.|
|unified agent| `src/productive_agents/agents/unified_agent.py` |Hook the compressor into position on the agent loop.|
|Guide Optimization Tips| `experiments/prompt_optimizer/unified_compress_update_history_prompt.py`, `unified_compress_update_observation_prompt.py` |Prompt template for updating compression guidelines in natural language space.|
|end-to-end pipeline| `experiments/appworld/run_ctxopt_pipeline.py:87` (`main`), `experiments/appworld/run_all.py` |Entrance to optimization and evaluation of reproduction guides.|
|Credential placeholder| `configs/private_config_dummy.yaml` |The upstream only provides placeholder keys, and you need to build`configs/private_config.yaml`yourself before running.|
