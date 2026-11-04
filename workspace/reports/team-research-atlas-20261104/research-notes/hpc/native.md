# Ask whether that mechanism helps the solver

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Does the preparation memory-policy change affect native OpenFOAM solver time when all solver inputs and settings stay fixed?

## Why investigate this?

The copy/hash qualification changed aggregate preparation counters. Completed native test 2294676 now measures whether changing only preparation-child policy affects solver time with matched Scotch inputs and runtime.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Preparation-child policy | Inherited policy; native solver launch and initialized Scotch source fixed. | Interleave-all policy for copy/hash child only; solver launcher parent remains unchanged. Four ABBA arms, 20 steps /19 measured intervals each. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| Terminal job | 2294676 COMPLETED 0:0; 2,200 seconds; one Iris node /56 ranks. |
| Inherited mean | 22.163497501 seconds/step (two equal-length arms). |
| Interleaved mean | 21.771496718 seconds/step; 1.768677456% lower pooled time. |
| Adjacent comparisons | B1 versus A1: +0.73172% slower; B2 versus A2: -4.20539% faster. |
| Native correctness | All four 20-step native replays pass; force-coefficient trajectories identical; source/payload gates pass. |
| Cost | 34.222222 allocated CPU-hours, conservatively 35 planning hours; billed SU unknown. |
| Actual confirmation | 2294735 accepted; 40 steps /39 intervals per arm, BAAB, maximum2hours /112 allocated CPU-hours. |

## What did we learn?

- The pooled mean favors interleaved preparation, but adjacent pair signs disagree. This is a short directional signal, not a stable optimization.
- Control repeat drift is +2.61343%; candidate repeat drift is -2.41591%. B1 has a wider maximum step than either control.
- Five-second whole-node diagnostics were collected: 95–98 samples per arm. CPU/I/O/memory pressure files were unavailable; missing pressure is not zero.

## Decision

Do not promote the 20-step signal. Reversed 40-step BAAB confirmation 2294735 was accepted on 4 November 2026; its 12:36:04 UTC snapshot was RUNNING on iris001. Review all four completed arms before deciding; no new performance result yet.

## Limits and remaining questions

- One short ABBA allocation does not eliminate nonlinear drift or prove a roughly 1.77% effect.
- Only preparation-child policy changes; per-rank memory policy, per-file residency and hardware bandwidth were not measured.
- Iris seconds cannot establish a gain on NSCC or Gadi. This result does not compare against the teammate recipe.

## Sources

- [Completed native result and interpretation](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/hpc-experiments/iris-preparation-native20-20261103/completed-2294676/RESULTS.md)
- [Independent native replay](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/hpc-experiments/iris-preparation-native20-20261103/completed-2294676/independent-native-replay.json)
- [Detailed telemetry review](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/hpc-experiments/iris-preparation-native20-20261103/completed-2294676/REVIEW.json)
- [Confirmation receipt and frozen job](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/hpc-experiments/iris-preparation-reverse40-20261104/STATUS.md)
