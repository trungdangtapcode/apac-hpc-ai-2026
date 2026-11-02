# Partial in-solver telemetry, not a completed comparison

Capture: 3 November 2026, 02:25:40 Vietnam. S1 Scotch has 19 measured intervals (33.672468410 s/step); X1 xyz has only 11 (25.421571143 s). The job is still active and the full four-arm comparison is unavailable. No improvement claim or budget retirement follows from these numbers.

All 13 individually captured files replay their hashes. ANALYSIS.json and replay.py reproduce sample counts, memory extrema, counter deltas and observed log intervals. No atomic multi-file capture or independent complete native-output validation is claimed.

The new evidence shows MemAvailable reaching 39.58/41.44 GiB during execution, rather than the 162–168 GiB endpoint values. Swapping was absent in sampled counter deltas, and PSI files were unavailable. Reclaim does not consistently track step speed; node-wide counters and uncertain native clock alignment cannot establish per-rank causes.

[Updated mechanism hypotheses and decisions](/home/apacsc42/workspace/reports/hpc-next-directions-20261103/MECHANISMS.md).
