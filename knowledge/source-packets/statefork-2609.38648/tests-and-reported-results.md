# StateFork reported results and review boundaries

Fixed paper `2609.38648v1`: §2.2 state boundary; §3.1–3.3 / PDF pp.6–7; §4 Waypoint; §5.2 / pp.11–12; Appendix A evaluation conditions.

The paper reports MCTS task-completion improvement of about 26% relatively and up to 70% under its world-node budget, Terminal-Bench setup, 77 tasks and respective configurations. This is not the project's shared TB2 30/19/40 protocol. Smart Decider versus eager reports 23% lower average completion time and 58% lower storage; these are paper system results, not local transfer gains of individual mechanisms.

Historical adaptation comparison: the paper estimates C_phys = alpha*m + beta and compares cumulative C_replay. Pinned `StateFork/decider/decider.py` has a `ThresholdDecider` default of 5 seconds without that linear model. The local adaptation used caller-supplied estimated costs and the paper decision rule; it did not calibrate alpha/beta automatically or reproduce the backend. Pinned Waypoint requires Linux, root, CRIU/OverlayFS and a fork-capable CLI. The original paper experiment commit is unknown; the selected backend cannot automatically be equated to it.

Official test execution and full upstream reproduction remain unknown/not performed. See [configuration and examples](configs-and-examples.md). A prior independent local adaptation passed 5 synthetic functional tests; this is a historical report, not a new run, official test, H0 migration or measured transfer benefit. Real CRIU/Waypoint physical recovery remains unverified.
