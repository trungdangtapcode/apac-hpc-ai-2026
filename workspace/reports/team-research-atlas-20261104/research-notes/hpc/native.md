# Confirm preparation policy with reversed order

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Does the preparation-policy signal survive reversed order and a longer native solve?

## Why investigate this?

The 20-step ABBA screen gave a small pooled signal with conflicting adjacent signs. The 40-step BAAB confirmation checks both order sensitivity and longer work with the same source, solver and child-only treatment.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Horizon and order | 2294676: 20 steps /19 intervals, ABBA. | 2294735: 40 steps /39 intervals, BAAB; same Scotch source, 56 ranks, runtime and sampling. |
| Treatment | Inherited preparation-child memory policy. | Interleave-all preparation-child policy; solver launcher remains unchanged. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| Terminal state | 2294735 COMPLETED 0:0; 4,710 seconds, Iris001 /56 CPUs. |
| Candidate B1 /B2 | 21.842916421 /21.881843121 seconds/step. |
| Control A1 /A2 | 29.418802008 /33.586912671 seconds/step. |
| Pooled within-job contrast | 21.862379771 versus 31.502857339 seconds/step; 30.601914818% lower time. |
| Adjacent changes | −25.75185% /−34.85009%; both favor candidate. |
| Repeat drift | Candidate +0.17821%; control +14.16819%. |
| Correctness | Four 40-step native replays pass; 39 timings each; force-coefficient trajectories identical; source/payload/runtime gates pass. |
| Cost | 73.266667 allocated CPU-hours, conservatively 74 planning hours; billed SU unknown. |

## What did we learn?

- The reverse 40-step result favors interleaved preparation in both adjacent comparisons, stronger than the earlier 20-step screen.
- The measured effect changes from 1.77% to 30.60% across allocations; control drift and nonlinear order effects prevent treating 30.60% as a stable or universal speedup.
- Reported candidate means repeat closely; this does not establish a causal page-placement explanation or a gain against the teammate recipe.

## Decision

Retain 2294735 as a strong within-job signal with variable effect size. Independent same 40-step ABBA confirmation 2294800 is accepted; at 4 November 15:08:11 UTC it was RUNNING on iris001. No completed metrics exist for 2294800 yet; do not assign prior results to it. No universal 30.6% or official 150-step claim.

## Limits and remaining questions

- BAAB places candidates outside the central controls; nonlinear drift or endpoint effects remain possible.
- Per-rank memory policy, per-file residency and hardware bandwidth were not measured. Pressure files are unavailable, not zero.
- Different platforms and allocations cannot be ranked by raw seconds; no Gadi/NSCC gain is inferred.

## Sources

- [Completed reverse 40 native review](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/hpc-experiments/iris-preparation-reverse40-20261104/completed-2294735/RESULTS.md)
- [Independent 40-step replay](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/hpc-experiments/iris-preparation-reverse40-20261104/completed-2294735/independent-native-replay.json)
- [Earlier 20-step review](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/hpc-experiments/iris-preparation-native20-20261103/completed-2294676/RESULTS.md)
- [Actual same-horizon confirmation receipt](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/hpc-experiments/iris-preparation-repeat40-20261104/STATUS.md)
