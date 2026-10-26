# ReasoningBank reported results and review boundaries

Fixed paper `2509.25140v2`: §3.2 / PDF pp.4–5; Appendix A.1–A.2 / pp.21–22; Table 1 / p.7; Appendix C.2, Table 5 / p.27.

Table 1 reports WebArena / Gemini-2.5-Flash: No Memory → ReasoningBank success 40.5% → 48.8%, average steps 9.7 → 8.3. Table 5 reports total tokens 50,847.4 → 53,054.5 (about +4.3%), including action generation, judging and extraction. The token typography was corrected against the fixed paper text, lines 1672 and 1678, on 2026-10-22. These are base ReasoningBank system results without MATTS, not causal gains from one memory operation.

Historical adaptation comparison: the paper learns continuously on a test-task stream; the local adaptation restricted updates to permitted train experience and froze memory before dev/test. The pinned `WebArena/memory_management.py` initializes Vertex/GenAI clients on import; the historical local module avoided cloud initialization. Judge/extractor/embedding interfaces were explicitly injected and their costs assigned to the caller. Retrieval granularity, provenance checks and JSON freezing were local design differences.

Official test execution and full upstream reproduction remain unknown/not performed. The [configuration page](configs-and-examples.md) retains official entries. A prior independent local adaptation passed 5 synthetic functional tests; this is a historical report, not a new run, official test, H0 migration or measured transfer benefit.
