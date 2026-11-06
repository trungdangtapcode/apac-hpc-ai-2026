# Iris job 2295087 review

**Review status: valid complete matched configuration comparison.** This is not
a candidate win. The Slurm job completed with exit code `0:0` after 5,430 s on
`iris001` with 56 allocated CPUs. Execution order was 48-rank control, balanced
40-rank candidate, balanced 40-rank candidate, 48-rank control (ABBA).

| Arm | Ranks | Steps | Timed intervals | Mean time |
|---|---:|---:|---:|---:|
| A1 control, default mapping | 48 | 40 | 39 | 27.549682806 s/step |
| B1 candidate, socket/core | 40 | 40 | 39 | 40.020672136 s/step |
| B2 candidate, socket/core | 40 | 40 | 39 | 22.901997128 s/step |
| A2 control, default mapping | 48 | 40 | 39 | 31.794129632 s/step |

Equal-weight pooled means are **31.461334632 s/step for the candidate** and
**29.671906219 s/step for control**: the candidate is **6.030716% slower** in
this comparison. Candidate repeat drift is **−42.774581%** from B1 to B2;
control drift is **+15.406518%** from A1 to A2. Retain this as a valid but
high-variance matched comparison. Do not promote the candidate or claim it is
competitive with the separate historical 22-second observation.

## Gate review

Replay verified the raw archive SHA-256 and all **452** collected file hashes,
plus all **101** frozen payload hashes. Payload checks before and after,
accepted-source checks before and after for both decompositions, source-after
checks, and runtime library/tool identity checks pass. `native_output.py`
passes for all four arms: each log reaches `End`, records exactly steps 1–40
and 39 positive timings, agrees with wall-clock function-object values and
fixed iteration counts, contains 40 finite force-coefficient rows, and has
resource return status 0.

All four strict per-rank proof sets pass. The separate actual placement
preflight and both candidate arm proofs show **20/20 ranks across NUMA nodes
0/1**. B1 and B2 have identical rank-to-CPU masks. These are pre-MPI launcher
affinity records; they do not establish solver helper affinity or memory page
placement. Since identical candidate masks yielded means of 40.02 and 22.90
s/step, placement alone cannot explain the drift.

## Diagnostics and limits

Five-second whole-node telemetry was collected for all arms (230, 329, 193,
and 263 samples, respectively); samplers stopped successfully. B1 and B2 had
similar median aggregate CPU frequency (~3,300 MHz), while the median sampled
minimum across CPUs was ~2,900 MHz for B1 and ~3,299 MHz for B2. Their median
`MemAvailable` values were about 59.6 and 59.8 million KiB. These aggregates
are not process attribution or causal bandwidth evidence; procfs pressure
files were unavailable. Missing site-billed SU remains unknown.

`partial-results.json` is the last progress snapshot, written before final source/runtime checks; its `complete: false` describes that phase. The final `comparison.json` has `passed: true` and `complete_four_arm_comparison: true` after all gates. `scored_result: false` is intentional: this is a research microbenchmark, not an official contest score. No frozen evidence is rewritten to change these states.

Root additionally replays every actual rank file (216 records across five groups), both same-partition force-repeat checks (zero maximum difference), time-zero fields against accepted sources, and all 101 local frozen file hashes; see `ROOT_REPLAY.json`.

Replay with `python3 replay_review.py`. It verifies integrity, gates, all four
native arms, exact candidate rank masks, NUMA placement counts and telemetry
summary, then writes `REVIEW.json`.
