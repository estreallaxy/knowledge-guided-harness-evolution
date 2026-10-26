# AgentRewind reported results and review boundaries

Fixed paper `2608.14380v1`: framework / PDF pp.2–4; external-environment recovery boundary / p.4; Table 2 / p.6; Appendix B–C budget and implementation notes.

Table 2 reports Terminal-Bench 2.0 Continue 78.7%, AgentRewind 83.1%. The original protocol has no preset total wall-clock, step or token bound; rewinding/repeated submissions can obtain acceptance feedback. This is not a gain under this project's fixed budget and sealed-test protocol. The DeepSeek-V4-Flash Continue column is not an AgentRewind gain for that model. The official alpha does not include the private benchmark harness/data.

Historical adaptation comparison: the original uses an external bare Git repository/private index to track and restore workspace state. The local adaptation used file copies and SHA-256 and restored only into a new directory. It did not implement the rewind monitor/automatic selection, model suffix generation or original recording/replay system. Preserving cumulative usage, explicit recovery boundaries and non-overwriting sources were local designs; no H0 integration was completed. Workspace/context recovery does not establish recovery of external services, processes or judge state.

Official test execution and full upstream reproduction remain unknown/not performed. See [configuration and examples](configs-and-examples.md). A prior independent local adaptation passed 5 synthetic functional tests; this is a historical report, not a new run, official test, H0 migration or measured transfer benefit.
