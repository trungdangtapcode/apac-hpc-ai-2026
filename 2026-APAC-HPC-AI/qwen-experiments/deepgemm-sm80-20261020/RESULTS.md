# 80-SM boundary pilot submitted

Updated 2026-10-20T09:23:02.323548+00:00. H100 **222279.pbs111** is **R** at the retained query; one node, eight GPUs, ten minutes, maximum **170.666667 SU**. No result is available for SM80. [Receipt](pbs-receipts.json), [live PBS](live-pbs.txt), [plan and fixed acceptance rule](PLAN.md).

The preceding **222277** passes all **240 full cases**, six separate provider-preflight cases, numerical/input/source/default-restoration/UUID guards and six actual native SM90 templates. Settings 120/96 fail the declared consistent 5% rule, so **132 remains the serving default**. At M54 alone, 96 reduces QKV/O-proj helper latency by 2.73%/2.65% on 8/8 ranks; other M values are mixed and O-proj M32 regresses 5.99%. These are synthetic kernel timings, not model throughput. [Every setting/rank, units and limits](../deepgemm-sm-screen-20261020/RESULTS.md).

The new candidate 80 targets the logical 80-tile QKV boundary observed in those traces; it is one geometry-supported point with a fresh 132 control, not a wide scan or unchanged 96/120 retry. Exact benchmark/cache code and numerical/graph controls are byte-identical to validated 222277. Four unranked provider-preflight cases precede 160 full cases; four actual traces must prove 132/80 kernel activation. [Tile evidence](tile-evidence.json), [payload validation](validation.json). Both shapes and M32/48/54/60/64 remain; no gate relaxed. This point closes the tested scheduler-budget family if it fails. A micro gain would still need safe caller/integration review and an independent full-model experiment.

Published Used **37439.430 SU**, Balance **26560.570 SU**, In Doubt **0.000 SU**, queried 2026-10-20T09:21:46.816377+00:00. Prior 222277 charge reconciles 37.262 SU and all older maxima are released. Reserve only the new maximum **170.666667 SU**; internal headroom **13389.903333 SU**, unchanged 51000 cap/13000 buffer. [Fresh accounting proof](accounting-preflight.json). No prepaid double subtraction or uncertain retry.

H200 **24990/24928/24962/24964/24965** all remain Priority-pending, cap five. No cancellation or sixth job. H100 only 222279 is active. Model bests remain H200 3022.034919 and H100 2433.019859 good output tokens/s, with official full-set reference accuracy unverified. No model/SLA/quality claim, package change, authentication restart or background Codex. [Live H200](live-slurm.txt).

## Completed 80-SM test — 2026-10-20T09:26:13.430145+00:00

**222279 passes all 160 full cases**, four separate provider-preflight cases, all eight numerical/input/source/UUID/default-restoration guards and four actual native 132/80 kernel traces. Exit 0, walltime **00:02:04**, estimated charge **35.271111 SU**, not yet reconciled; retain full maximum reservation. [Structured review](222279.pbs111-review.json), [sealed raw evidence](collect-222279.json).

| Shape | M | 132-SM control (us) | 80-SM (us) | Paired latency reduction (%) | Faster ranks /8 |
|---|---:|---:|---:|---:|---:|
| tp8-o-proj | 32 | 5.183 | 5.432 | -5.01 | 0 |
| tp8-o-proj | 48 | 5.373 | 5.472 | -1.98 | 0 |
| tp8-o-proj | 54 | 5.568 | 5.494 | +2.40 | 6 |
| tp8-o-proj | 60 | 5.396 | 5.367 | +1.34 | 5 |
| tp8-o-proj | 64 | 4.990 | 5.189 | -3.99 | 0 |
| tp8-qkv | 32 | 7.860 | 7.868 | +0.06 | 5 |
| tp8-qkv | 48 | 7.906 | 7.662 | +3.01 | 4 |
| tp8-qkv | 54 | 8.671 | 8.222 | +5.17 | 8 |
| tp8-qkv | 60 | 8.313 | 8.102 | +1.77 | 5 |
| tp8-qkv | 64 | 7.880 | 7.829 | +0.56 | 8 |

Candidate 80 fails the unchanged consistent 5% rule. At M54, QKV improves 5.17% on 8/8 ranks, O-proj only 2.40% on 6/8; other batches are inconsistent and M32 O-proj regresses 5.01%. **Keep 132; close the tested 96/120/80 scheduler family.** The targeted tile hypothesis produced one useful local signal but no safe general replacement. Do not selectively apply a global budget to a model or relax the gates. No further automatic SM scan or unchanged retry.

Move to a distinct model-level question with stronger interaction precedent: H100 prefill HPC-Ops with chunk 8192 versus the current both-phase HPC-Ops/chunk 4096 at fixed N54. The earlier h100-hpc-chunk 8192-29 only set chunk 8192 and checkpoint prefetch for prefill, retaining native auto MoE there; its worker explicitly applies HPC-Ops only to decode. Therefore the prior auto-prefill loss does not answer this missing HPC-Ops interaction. Prepare a fresh equally observed 4096/8192 pair, unchanged full protocol/output gates and default 132-SM dense path; no micro-derived model tweak. H200 has its own separate pending interaction pair, no cross-platform conversion.
