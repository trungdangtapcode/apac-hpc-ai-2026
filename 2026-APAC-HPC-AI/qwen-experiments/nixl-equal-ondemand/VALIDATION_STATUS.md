# Validation status after job 24375

Updated 17 October 2026. This note supersedes any inference that previous GPU execution or CPU byte-range tests establish full model correctness.

The immutable historical records retain their original scope: 936 byte-range cases and five fallback guards passed, and job 22809 completed GPU serving and a benchmark. Those records do not establish complete output equivalence or official accuracy.

New TP8/EP2 prefill candidate 24375 used the exact equal-TP patch and warmed its P/D connection successfully. It then failed the N56 latency gate (1.9978% joint SLA), short nonregression (0/8, seven new failed cases versus baseline) and long retrieval (11/12). It is rejected. The exact cause is not isolated between topology, model/backend execution and transfer. Do not attribute the regression uniquely to the patch or promote this configuration based on old geometry tests. No unchanged retry is justified.

Preserve the raw artifacts in ../runs/24375/ and review research-followup-20261017-2335/RESULTS.md before any future equal-TP experiment. This finding does not by itself establish a defect in the different, reviewed heterogeneous-TP configuration.
