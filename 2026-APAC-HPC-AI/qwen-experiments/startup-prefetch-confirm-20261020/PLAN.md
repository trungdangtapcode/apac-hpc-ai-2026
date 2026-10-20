# Independent reverse-order startup-prefetch confirmation

The first pair 222407/222408 passes all local serving and node-prefetch gates. Prefetch readiness is 436 s versus 602 s and allocated time 759 s versus 934 s (-18.737%, estimated 99.556 SU saving), while good output tokens/s changes 2411.827128 to 2395.929777 (-0.659%). The same benchmark/worker settings are retained. Different nodes, unknown initial page-cache state and control-first order confound causal interpretation; see the complete first-pair review in startup-prefetch-20261020.

Run exactly one independent reversed pair: candidate 76 (read) first, then control 77 (off). All prior execution files are byte-identical to their respective accepted payloads; only job/config provenance labels change. Both still include the same bounded per-node stage, full official 60/120/30 workload at N54, source/runtime/precision/transport/output gates, matched resource samples and separate post-score profiles. Prefetch time remains included in the readiness counter and allocation cost. No cache flush, new image, engine change, scoring tweak, seed change or model-quality relaxation.

## Predeclared assessment

Use the off run as the control regardless of execution order; the paired reviewer explicitly orders results by paired_role. Require every full local serving and sealed startup gate, two complete node receipts, exact common weights/index/helpers and declared read/off modes. Inspect all raw tails/errors, queue/batch/KV state, role hardware/node observations and native runtime/transport/profiler limits.

For this confirmation, a useful cost signal requires at least 10% lower allocated walltime/SU for read versus off, lower topology-script-to-ready time including the read, and no more than 2% lower goodput, with both runs qualifying. These thresholds are prospective for this repeat; they do not rewrite the first-pair plan. Record topology-script readiness separately from PBS prologue/full allocation timing. A passing repeat supports a repeatable practical saving, but two unmatched-node jobs still do not prove cold-cache causality or guarantee every allocation. If the direction fails or scoring materially regresses, close or mark inconclusive instead of scheduling automatic repeats. H100/H200 serving peaks and official full-set accuracy claims remain unchanged.

## Queue and maximum cost

Two serial 16-H100/30-minute jobs, 1024 SU each / 2048 SU maximum. First afterany static probe 222412, second afterany first; preserve one running allocation and at most three active jobs. The probe is independent hardware discovery, not a control member. Preserve the four H200 model positions. Fresh queue and project ledger under the budget lock must reconcile any posted costs of 222407, 222408 and 222412 before reserving; unposted jobs keep full maxima. Keep total used plus reservations below 51000 SU and retain 13000 SU project buffer. No uncertain submission retry or additional batch is allowed by this plan.
