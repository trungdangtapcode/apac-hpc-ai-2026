# NSCC single-rank trace admitted

**26004608.pbs101** was admitted with a definite receipt at 12:42 UTC on 26 October. At 13:01 UTC it was Q/q5, waiting for node_pool. Four nodes, 512 ranks, five-minute maximum, 42.666667 SU maximum. It observes one rank's affinity syscalls and compares against an untraced control. No solver or affinity mutation is included.

The first admission check failed before qsub because the previous review lacked an explicit passed field. The replay now writes passed only after all checks complete, and was rerun before successful admission. There was no earlier job or duplicate reservation. Exact sources, receipt and admission checks are retained.
