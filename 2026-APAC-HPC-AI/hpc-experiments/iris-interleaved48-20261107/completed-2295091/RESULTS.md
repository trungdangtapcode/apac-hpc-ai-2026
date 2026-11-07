# Reviewed interleaved rank-order result — 7 November 2026

Iris job **2295091** completed successfully on iris001: 4,861 seconds, 56 allocated CPUs, zero GPUs. This is a complete four-arm BAAB native comparison, each arm 40 steps and 39 timed intervals.

| Arm | Placement | Mean time (s/step) |
|---|---|---:|
| B1 | Alternating NUMA rank order, 24/24 | 23.473843110 |
| A1 | Default | 27.513559057 |
| A2 | Default | 32.555344669 |
| B2 | Alternating NUMA rank order, 24/24 | 26.748581194 |
| Candidate pooled | Two B arms | 25.111212152 |
| Control pooled | Two A arms | 30.034451863 |

The candidate takes **16.391975% less time** than its matched control; both adjacent comparisons favor it. This is a positive within-allocation result, not a stable global winner. It does not beat the separate 21.085908 s/step seed as an absolute observation. Both candidate and control drift substantially, so independent confirmation remains necessary.

Only the requested rank mapping changes: `--map-by ppr:24:package --rank-by span --bind-to core`. Actual proofs verify alternating NUMA membership and the same CPU set 0–47. Source decomposition, native runtime, fixed numerical work and uncollated I/O remain unchanged. The comparison JSON retains the inherited generic “balanced socket/core” question label; the frozen command and actual rank proofs establish the explicit PPR/span treatment. That label is not used to infer treatment identity.

Independent root replay verified 469 raw hashes, 57 frozen payload hashes and 240 actual rank records. Full source, field, native output, fixed work, runtime and force checks pass. Same-treatment force repeats have zero recorded difference; cross-treatment maximum absolute delta is 1.63966e-14. See `REVIEW.json` and `ROOT_REPLAY.json`.

Whole-node sampling was collected and inspected through the review, but cannot attribute pages or causal bandwidth limits to individual MPI ranks. Per-process residency was not collected in this job. No conclusion that NUMA placement causes the speedup is warranted.

Actual allocated CPU time is 75.615556 CPU-hours, conservatively charged 76 planning hours. The old 140-hour reservation was retired once: ledger 1,914 consumed, zero reserved, internal stage 1,978. Site billed SU is unknown.

## Next decision

Retain this positive rank-order branch. Following the owner correction, prioritize exact repeats of the 21.085908 seed and process-level locality diagnostics before more blind mapping variants. A pooled loss closes promotion, not investigation of its fast state.

## Additional telemetry inspection

The reproducible `inspect_telemetry.py` and `TELEMETRY_INSPECTION.json` retain the inspected diagnostics. B1/A1/A2/B2 have 196/229/269/222 five-second samples, median sampled node CPU frequency about 3,300 MHz in each arm, and minimum node MemAvailable 41.065/40.800/43.651/40.681 GiB. Whole-node NUMA allocation-miss deltas are 118,712,282 /112,151,213 /25,588,061 /170,102,728. Launcher-tree major faults are 99,243 /5,903 /66,908 /194,833.

These do not order monotonically with solver speed: B1 is fastest despite more faults than A1, and A2 is slowest despite the lowest allocation-miss count. This weakens a simple single-counter explanation and supports process-attributed residency measurement. Whole-node NUMA misses are allocation-placement counters, not measured remote-read bandwidth. PSI and individual solver memory residency are unavailable in this job; missing values are not zero. No GPU metrics apply to this zero-GPU CPU trial.
