# Submitted followups and H100 profile — 19 October 2026

The user requested continued optimisation. The [plan](PLAN.md) explains each hypothesis, comparison, acceptance rule and resource bound. All six returned job IDs were recorded immediately, and the two PBS jobs have a verified serial dependency. No background AI or automatic retry was enabled.

| Platform | Job | Trial | Requested maximum allocation |
|---|---|---|---|
| H200 | 24721 | Fresh DeepGEMM prefill chunk 8192, auto decode, N58 control | 16 GPUs / 17 min |
| H200 | 24722 | Same serving configuration, N60 | 16 GPUs / 17 min |
| H200 | 24723 | Same N58 control with prefill chunk 12288 | 16 GPUs / 17 min |
| H200 | 24724 | Same N58 chunk 8192 control with HPC-Ops decode | 16 GPUs / 17 min |
| H100 | 221589.pbs111 | Independent both-phase HPC-Ops N52 repeat | 16 GPUs / 45 min |
| H100 | 221590.pbs111 | Same serving configuration, N54; afterany 221589 | 16 GPUs / 45 min |

At submission verification, H200 jobs were pending Resources (later Priority); PBS 221589 was queued and 221590 dependency-held. These are waiting states, not benchmark results. Preserve their queue positions. Maximum new PBS reserve is 3072 SU; the last freshly queried ledger reports Used 27199.147, Balance 36800.853 and In Doubt 0 as of 19 October 12:00:01 SGT. Internal operating headroom after the new reservation is 20728.853 SU under the unchanged 51000-SU operating bound, with a 13000-SU buffer. Those limits are internal planning, not organiser quotas or actual charges for this batch.

Corrected a bookkeeping inconsistency before reserving: the previous status turn reconciled the three old jobs in `jobs` and the ledger, but left their entries in `pending_reservations` as pending. Fresh terminal accounting and the unchanged Used total verify they are already charged. Their pending reservation states are now also RECONCILED_IN_LEDGER, preventing a duplicate conservative deduction. This correction does not increase the research budget.

## What the recovered profile establishes

Job 221346 supplies a separate post-score N48 diagnostic, with four prefill steps and 32 decode steps. All 16 expected ranks have nonzero kernel events and sealed hashes; all 376 diagnostic requests succeeded. It is not the scored N50 traffic and does not measure N52/N54 performance.

| Role | Named HPC-Ops grouped FP8 GEMM share | Other leading kernels |
|---|---:|---|
| prefill-0 | 33.812% | One NCCL Ring BF16 all-reduce kernel 22.784%; FlashAttention kernel 7.344%; HPC-Ops reduction 6.874% |
| prefill-1 | 33.259% | One NCCL Ring BF16 all-reduce kernel 24.007%; FlashAttention kernel 7.232%; HPC-Ops reduction 6.759% |
| decode-0 | 22.888% | FlashInfer paged attention 16.172%; two MNNVL collectives 11.566% and 11.176%; per-token quantisation 9.993% |

These percentages divide summed event durations across ranks by summed kernel durations in that role. They are not elapsed critical-path shares. Do not sum them into an end-to-end speed prediction or attribute every quantisation kernel to MoE. Named HPC-Ops activation/reduction kernels are present too; grouped GEMM alone is not the complete MoE share. Actual names and per-rank hashes are retained in `h100-both-phase-profile.json`.

The trace motivates investigating prefill communication after the current trials. NVIDIA documents that `NCCL_ALGO` can select Ring or Tree, defaults to automatic selection and supports per-collective selection from NCCL 2.24. Restricting algorithms can fail when none is valid. [NVIDIA NCCL environment variable reference](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/env.html#nccl-algo).

A possible next hypothesis is changing only prefill all-reduce selection while preserving decode MNNVL. This is not yet a submitted experiment: first establish the exact NCCL version and that SGLang's active prefill communicator honours the setting, check earlier trials for duplication, and define a same-platform control. A kernel share on H100 does not establish an H200 gain, and automatic algorithm selection may already be better. No new PBS credit is committed to this branch.

## Next review

Review each completed run independently; do not wait for unrelated pending jobs. Compare 24722/24723/24724 with 24721, and 221590 with the N52 repeat 221589. Require full terminal seals, exact submitted payloads, unchanged full-duration protocol, correct runtime and rank coverage, zero request errors/cancellations, the joint latency gate, short nonregression and all 12 long retrieval checks. No automatic higher load or unchanged backend/output-failure retry. Useful gains need independent confirmation before promotion.

The source measurements remain 2780.483 good tokens/s on H200 24647 (original peak 2786.696) and 2398.728 on H100 221341. The new jobs have no score yet. Full organiser accuracy remains unverified: the rules require at least 99% of the organiser's unmodified FP8 reference benchmark score, not matching output text or passing these synthetic diagnostics. Establish the actual organiser evaluation tasks, harness settings and reference before claiming accuracy or scheduling a surrogate full-set check. No slide, official submission package, HPC task or organiser upload changed.
