# Independent reverse-order startup-prefetch confirmation

The first pair 222407/222408 passes all local serving and node-prefetch gates. Prefetch readiness is 436 s versus 602 s and allocated time 759 s versus 934 s (-18.737%, estimated 99.556 SU saving), while good output tokens/s changes 2411.827128 to 2395.929777 (-0.659%). The same benchmark/worker settings are retained. Different nodes, unknown initial page-cache state and control-first order confound causal interpretation; see the complete first-pair review in startup-prefetch-20261020.

Run exactly one independent reversed pair: candidate 76 (read) first, then control 77 (off). All prior execution files are byte-identical to their respective accepted payloads; only job/config provenance labels change. Both still include the same bounded per-node stage, full official 60/120/30 workload at N54, source/runtime/precision/transport/output gates, matched resource samples and separate post-score profiles. Prefetch time remains included in the readiness counter and allocation cost. No cache flush, new image, engine change, scoring tweak, seed change or model-quality relaxation.

## Predeclared assessment

Use the off run as the control regardless of execution order; the paired reviewer explicitly orders results by paired_role. Require every full local serving and sealed startup gate, two complete node receipts, exact common weights/index/helpers and declared read/off modes. Inspect all raw tails/errors, queue/batch/KV state, role hardware/node observations and native runtime/transport/profiler limits.

For this confirmation, a useful cost signal requires at least 10% lower allocated walltime/SU for read versus off, lower topology-script-to-ready time including the read, and no more than 2% lower goodput, with both runs qualifying. These thresholds are prospective for this repeat; they do not rewrite the first-pair plan. Record topology-script readiness separately from PBS prologue/full allocation timing. A passing repeat supports a repeatable practical saving, but two unmatched-node jobs still do not prove cold-cache causality or guarantee every allocation. If the direction fails or scoring materially regresses, close or mark inconclusive instead of scheduling automatic repeats. H100/H200 serving peaks and official full-set accuracy claims remain unchanged.

## Queue and maximum cost

Two serial 16-H100/30-minute jobs, 1024 SU each / 2048 SU maximum. First afterany static probe 222412, second afterany first; preserve one running allocation and at most three active jobs. The probe is independent hardware discovery, not a control member. Preserve the four H200 model positions. Fresh queue and project ledger under the budget lock must reconcile any posted costs of 222407, 222408 and 222412 before reserving; unposted jobs keep full maxima. Keep total used plus reservations below 51000 SU and retain 13000 SU project buffer. No uncertain submission retry or additional batch is allowed by this plan.

## Definite execution checkpoint — 2026-10-20T14:06:36.113310+00:00

# Reverse-order startup confirmation submitted

The first accepted pair saves 18.737% scheduler-reported walltime (934→759 seconds), with goodput 2411.827128→2395.929777 (-0.659%). Model/runtime/protocol/output and sealed startup gates pass, but nodes differ and cache state is unmeasured; do not promote a cost guarantee from one comparison.

New definite jobs: **222419.pbs111 read first → 222420.pbs111 off second**, after static probe 222412. The server confirms serial afterany dependencies. At the submission snapshot the static probe is running and both new model jobs are held; later static snapshots show exiting, not yet terminal-sealed. Each model allocation is 16 H100 / 30 minutes / maximum 1024 SU, combined maximum 2048 SU. The workers, full official scoring, precision, model, transport, output checks, matched samples and separate profiles remain identical to the accepted first pair. [Receipts](pbs-receipts.json), [server states and dependencies](pbs-post-submit.txt), [prospective thresholds](PLAN.md).

The prospective confirmation gate requires at least 10% lower scheduler-reported walltime/SU and lower topology-script-to-ready time, no more than 2% lower goodput and all full local gates. Review order follows control/candidate roles regardless of launch order. If it fails, close or mark inconclusive; this is not an automatic repeated sweep. A passing repeat still cannot prove cold physical storage causality on unmatched nodes.

The fresh ledger reconciles the preceding 963.129 SU charge exactly to the two walltime-derived costs within rounding. Published Used 41235.624 SU, Balance 22757.976 SU, In Doubt 6.4 SU at 22:00:02 server time. Retain the static probe maximum 6.4 SU and new 2048 SU reserve; internal headroom 7709.976 SU under the unchanged 51000 cap/13000 buffer. No prepaid deduction is counted twice. [Reconciliation](reconciliation.json), [raw pre-submit source](pbs-pre-submit.txt).

Four H200 model jobs 24928/24962/24964/24965 remain Priority-pending in the fresh Slurm snapshot; positions are untouched. Accepted H200/H100 serving peaks remain 3022.034919/2433.019859 good output tokens/s as separate hardware series. Official full-set accuracy remains unverified. No submission package, image, benchmark rule, authentication or background AI change.
