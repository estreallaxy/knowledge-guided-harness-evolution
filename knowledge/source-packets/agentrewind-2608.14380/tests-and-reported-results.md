# AgentRewind report results and review boundaries

Fixed paper`2608.14380v1`, original text location: Framework/PDF pp.2–4; External Environment Recovery Boundary/p.4; Table 2/p.6; Appendix B–C budget and implementation instructions.

Table 2: Terminal-Bench 2.0 Continue 78.7%, AgentRewind 83.1%. The original protocol does not have a preset total wall clock, step or token upper limit, and rewind/repeated submission can obtain acceptance feedback, so it cannot be regarded as an improvement under the fixed budget and sealed test of this project. The Continue column of DeepSeek-V4-Flash is not the AgentRewind gain for this model. The official alpha explicitly does not include private benchmark harness/data.

Historical verification instructions for fixed code and local adaptation: The original external bare Git/private index tracking and recovery workspace; local adaptation uses file copies and SHA-256, and only restores to the new directory. Does not implement rewind monitor/automatic selection, model suffix generation or original recording and playback system. Retaining accumulated usage, explicit boundary declaration, and non-overwriting of sources are all local migration designs and have not yet been connected to H0.

Execution results of the official test: unknown; the complete upstream system is not running. Fixed official entry in README saved in [configs-and-examples.md]. Previously independent local adaptation passed 5 synthetic functional tests; these tests are neither official tests nor H0 migrations, gains, or full paper reproductions.
