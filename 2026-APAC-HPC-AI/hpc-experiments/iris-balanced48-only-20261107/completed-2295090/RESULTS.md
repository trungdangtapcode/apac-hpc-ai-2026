# Terminal review: Iris job 2295090

## Outcome

Job 2295090 completed on `iris001` with scheduler state `COMPLETED`, exit code `0:0`, 56 allocated CPUs, and 4,525 seconds elapsed. The four-arm native replay is complete and valid for this bounded 40-step comparison. It does not establish a stable mapping win or an official workload score.

| Arm | Mapping | Mean solver time (s/step) |
|---|---|---:|
| B1 | socket/core, 24 ranks per NUMA node | 32.001684128 |
| A1 | default | 24.663577539 |
| A2 | default | 24.200998556 |
| B2 | socket/core, 24 ranks per NUMA node | 21.085907685 |

The BAAB candidate mean is **26.543795906 s/step**; the default mean is **24.432288048 s/step**. Candidate time is **8.6423% higher**. The candidate repeats diverge sharply: B1 is slower than A1, while B2 is faster than A2. Although B2's 21.0859 s/step is below the historical approximately 22.35 s/step observation, one arm does not establish a stable best configuration. Do not promote this mapping.

## Integrity and native-work gates

Independent replay verified all **469/469** archived file hashes and the archive byte/hash seal. All **57 frozen payload entries**, the frozen runtime file hashes, and the complete accepted-source observation before and after the run match. Both source observations cover 909 complete files (896 core files); the final comparison records stable runtime identity.

Each arm has 40 solver time rows and 39 timed intervals. All four used 48 ranks, the same source and fixed iteration settings, and uncollated I/O. The pre-solver balanced probe and each arm's actual rank-proof JSON contain exactly ranks 0–47, each with one unique CPU affinity. Balanced proofs show 24 ranks on each observed NUMA CPU set. B1 and B2 have identical CPU-ID-by-rank maps, so their timing divergence is not explained by a changed recorded map.

All 288 initial decomposed field fingerprints at time zero match the same source field seal for every arm. Same-source force-coefficient trajectories pass the existing strict `math.isclose(rel_tol=1e-9, abs_tol=1e-10)` checks; the largest reported cross-arm absolute difference is approximately `1.63e-14`. These gates support a valid matched-work comparison; they do not identify why elapsed time varied.

The authoritative final comparison is `runs/2295090/comparison.json`. `runs/2295090/partial-results.json` is an intentionally incomplete progress snapshot (`complete: false`) retained from before the final arm; its incompleteness is expected and is not evidence of corrupted final metadata.

## Diagnostics and limits

The bundle includes runtime/environment logs, a hardware inventory, and five-second node-level resource sampling. CPU frequency was available to the collector, but the readings are not attributable to the solver task. CPU, memory, and I/O pressure stall information (PSI) was unavailable. The resource samples are node-wide, not process attribution. No causal claim about binding, memory placement, bandwidth, or frequency is supported by these observations.

This is one four-arm, 40-step microbenchmark allocation. The opposing adjacent comparisons and large candidate-repeat spread mean the pooled loss is the appropriate decision for this trial; the single fast B2 arm is not a repeatable improvement.

## Replay files

- `replay_review.py` independently checks the archive, frozen payload/runtime/source, rank records, native timing and field/force gates.
- `REVIEW.json` contains the machine-readable replay results.
