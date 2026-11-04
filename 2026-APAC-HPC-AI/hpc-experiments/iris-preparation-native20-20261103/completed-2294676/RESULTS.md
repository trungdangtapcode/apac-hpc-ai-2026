# Preparation-policy solver screen: small signal, not a promoted improvement

Reviewed **4 November 2026**. Iris job **2294676 COMPLETED 0:0**, 2,200 seconds, 56 CPUs on iris001. All 237 collected file hashes and frozen deployed payload hashes passed collection verification. Independent local replay passes all four native arm checks: exactly 20 steps, 19 timing intervals, fixed solver iteration counts, successful exit and identical force-coefficient trajectories. Source, input, preparation-policy, launcher-parent-policy and payload before/after gates return zero. The native comparison reports stable runtime identity.

## Hypothesis and control

The preceding copy/hash-only qualification 2294675 showed that interleaving the preparation child's allocations changed aggregate NUMA file-page distribution. The new test asks whether that preparation change helps the actual solver. All four arms use the same initialized Scotch source and unchanged solver command, 56 ranks, OpenFOAM v2512 double precision and physical problem. Only the copy/hash child's policy changes; per-rank solver policy is not measured. ABBA order: inherited, interleaved, interleaved, inherited.

| Arm | Mean s/step | Median s/step | Maximum s/step |
|---|---:|---:|---:|
| A1 inherited | 21.877619018 | 21.690479698 | 23.092117186 |
| B1 interleaved | 22.037702366 | 21.773315819 | 25.436449494 |
| B2 interleaved | 21.505291070 | 21.308845927 | 23.836183327 |
| A2 inherited | 22.449375985 | 22.270427108 | 23.643289745 |

Equal-length pooled control mean is **22.163497501 s/step** versus **21.771496718 s/step** for interleaved preparation: **1.768677456% lower time**. Adjacent comparisons disagree: B1 is **0.73172% slower** than A1; B2 is **4.20539% faster** than A2. Repeated controls drift +2.61343%; candidates drift −2.41591%. The short single-allocation screen therefore gives a directional signal, not a stable optimization or a causal explanation. It does not establish an improvement over teammate, NSCC or Gadi.

## Diagnostics and limitations

Five-second node sampling collected 96/97/95/98 samples across the four arms. Required CPU-tick, CPU-frequency, memory and vmstat sources are present; inspected samples report no collection errors. Median read cost is about 2.95–3.29 ms, maximum 4.12 ms. This is sampler duration, not measured performance interference. Reported median CPU frequencies are near 3.30 GHz in all four arms; this is procfs reporting, not effective-cycle or bandwidth measurement. Minimum available whole-node memory is approximately 38.5–41.5 GiB. CPU/I/O/memory pressure files are absent, so pressure is not collected, never zero or healthy. Hardware bandwidth, per-file page residency, per-rank memory policy and solver-helper affinity remain unmeasured. B1's maximum is worse than either control; retain that tail rather than removing it.

ABBA balances linear drift imperfectly and cannot eliminate nonlinear/order effects. Twenty steps are insufficient to promote a roughly 1.77% effect. Next justified question: does the same factor remain favorable with reversed BAAB order and a longer fixed horizon? Keep all other settings and instrumentation matched. This is a proposed derived test, not a submitted job. No new payload has yet passed admission review; do not resubmit the frozen parent or claim a receipt. Fresh shared-account queue check at **4 November 18:39:25 Vietnam** was empty. Existing independent job scripts are frozen one-shot bundles, not ready repeat submissions; a derived payload, seals, runtime checks and bounded reservation must be completed before another admission.

## Cost and preservation

Allocated cost is **34.222222 CPU-hours** (2,200 ×56 /3,600), conservatively 35 planning hours. The 70-hour maximum reservation was retired once under the Iris ledger lock. Ledger now records 1,024 consumed, zero reserved, stage 1,059. These are internal planning CPU-hours; billed SU remains unknown. NSCC/AI accounting and payloads are unchanged. Collection, native replay, detailed telemetry summary and scheduler receipt are retained alongside this review.
