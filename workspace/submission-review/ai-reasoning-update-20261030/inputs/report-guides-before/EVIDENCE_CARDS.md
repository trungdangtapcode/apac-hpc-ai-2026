# Three technical evidence cards

No new experiment is proposed by these cards. Rates are exported AIPerf Goodput in qualifying requests/s × 200.

## 1. Request-scoped KV transfer

**Environment:** organiser-provided H200 cluster; disaggregated Qwen. Selected roles are two TP4/EP1 prefills and one TP8/EP8 decode across two eight-GPU nodes. Official FP8 target and BF16 activation/KV remain.

**What happened:** early cold descriptor preparation scaled with the entire KV pool. Other layouts separately failed FP8 block alignment or warmup; these are different problems.

**Hypothesis and change:** inspect descriptor generation and make work proportional to transferred request pages, coalescing contiguous ranges. A representative geometry changes from about 403.8 million source entries per rank for the pool to 188 coalesced entries for a contiguous 4,000-token request.

**How we know:** source diffs/hashes, 720 heterogeneous-range checks, 936 equal-TP recovery checks, actual GPU transfer and independent semantic P/D routes are separate proof layers. Descriptor-count reduction is not an inference speedup ratio.

**What failed:** later superficially running equal-TP8/EP2 candidate 24375 had only about 1.9978% joint success and failed short-output checks. CPU geometry and server readiness were insufficient; the candidate was quarantined.

**Supported decision:** retain the validated request-scoped adaptation and require physical KV ownership plus response validation before scoring a new path.

**Limit:** no single matched whole-service experiment attributes the final approximately 3k level solely to descriptors. Early transport setup and later serving bottlenecks are different questions.

Sources: journal retrospective stages 5–7 and 26; native registration/semantic reviews; package patch metadata. Slides 7–8 and 22.

## 2. Backend interaction and an independent repeat

**Environment:** 16 H200, historical Slurm/Pyxis, disaggregated P4+P4 / D8-EP8, official FP8 target with observed BF16 KV. Full N60, requested 4,000/200, seed 2026, cold prefixes and 60/120/30. Both arms use DeepGEMM prefill/chunk 8192.

**Control and change:** fresh auto-decode 24912 versus HPC-Ops decode repeat 24913. This is the decode-runner change within that serving configuration. The team reused provided kernels; it does not claim to have invented HPC-Ops or FlashInfer.

| Metric | Auto control 24912 | HPC-Ops repeat 24913 |
|---|---:|---:|
| Good output tokens/s | 2838.853 | 2989.175 |
| Mean TTFT, ms | 822.293 | 947.627 |
| Mean request-mean ITL, ms | 16.579 | 14.934 |
| Joint SLA | 98.760% | 98.818% |

**Observation:** goodput improves about 5.295%; TTFT increases about 125.335 ms while ITL falls about 1.644 ms. The independent repeat is about 0.033% below original treatment 24738 at 2990.150791.

**Why profiling motivated the question:** separate N48 diagnostic 24819 retained 16 rank traces. Named group GEMM, MNNVL collective/RMSNorm and FlashInfer attention account for about 21.642%, 23.479% and 15.064% of summed recorded kernel duration. Those sums suggest investigation targets; they are not wall-clock fractions or predicted gains.

**Supported conclusion:** matched full model data and a treatment repeat support this operating-point interaction. Local output/retrieval checks pass. Official accuracy remains unverified.

**Limits:** the extended 24913 inspection has no dedicated continuous hardware series. Its server statistics cover the whole deployment and are event-weighted. A separate N48 trace cannot causally decompose the N60 gain. Do not claim measured FLOP saturation, a universal HPC-Ops advantage or an exact kernel-level explanation.

Sources: research-followup-20261020-0132/24913-review.json and inspection/24913.md; 24819 profile; original 24738. Slides 11–14.

## 3. Select N64 through full-protocol replication

**Environment:** 16 H200, historical Slurm/Pyxis, same disaggregated model, precision, topology and backends. Full requested 4,000/200, seed 2026, cold prefixes, 60/120/30. Operational source is held apart from load/identity/provenance; generated engine seeds vary.

| Metric | N62 control 25365 | N64 trial 25366 |
|---|---:|---:|
| Good output tokens/s | 3011.875113 | 3044.489701 |
| Good / all requests | 1855 / 1879 | 1876 / 1902 |
| Joint SLA | 98.722725% | 98.633018% |
| Mean TTFT, ms | 1037.629662 | 1110.463377 |
| Mean request-mean ITL, ms | 14.957663 | 15.002881 |

**Observation:** matched full goodput improves 1.082867%, while average TTFT and ITL rise modestly. Independent N64 repeat 25373 scores 3044.074628, about 0.013634% below the original.

**Why not keep increasing load:** the short N68 screen looked about 2.27% better; its matched full pair gained only 0.083056%. It missed the prospective useful-gain gate. Client concurrency is not actual decode batch size.

**How we know:** frozen source comparison, actual runtime/KV, raw joint-SLA denominator, zero errors/cancellations, local output checks and independent deployment repeats support the selected point.

**Hypothesis versus conclusion:** higher inflight load can change batching and queue pressure. Client TTFT and sparse gauges do not identify separate queueing, transfer and computation contributions. The local goodput advantage is measured; that causal latency decomposition is not.

**Decision:** keep reproduced N64. Historical three-run mean is 3044.400475. Later native 26766 at 3045.501509 is a separate runtime series. Highest complete cache point 27378 at 3048.446289 is only +0.240921% against its fresh control and is not promoted.

Sources: 25365/25366 full review; 25373 repeat; 25487/25488 full pair; 27376/27378 cache pair. Slides 12, 15, 21 and 24–25.
