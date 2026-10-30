# Evidence behind the decisions

These cards follow the seven-step reasoning flow. They are support material for the presenters, not an official question list. Research remains stopped.

## RQ 1 — how should 16 H 200 GPUs be distributed?

**Problem and constraints:** Qwen 3-235 B FP 8, two eight-H 200 nodes, fixed 4000/200 workload, per-request latency and output checks. A layout must fit compatible FP 8 partitions and complete useful requests.

**Baseline observations:** the topology record contains 14 measured original layouts plus three EP 2 replacements. Initial 07, 09 and the selected split differ in load/history; their scores are not a controlled one-factor ranking.

**Hypothesis and intervention:** trade replica count against TP width; keep TP groups within a node and allow separate prefill/decode implementations. Retain two TP 4/EP 1 prefills on node 0 and one TP 8/EP 8 decode on node 1 after usable measurements.

**Evidence and limit:** selected split measured about 1912.30 good output tokens/s atN 48 in the early series. This is a feasible measured decision, not proof every topology was compared under identical conditions or that it is globally optimal. FP 8 compatibility and real P/D response checks constrain eligibility. Main slides 3–5; backups 21–22.

## RQ 2 — what should we investigate first?

**Observation:** in the heterogeneous-TP recovery branch, job 22271 loaded model workers but pair warmup timed out at 360 s before any scored benchmark. This branch differs from the selected split.

**Source-level signal:** full-pool enumeration implied about 403.8 million source descriptor entries per rank, while one contiguous 4000-token request uses 188 coalesced ranges. This describes different scopes, not a speed ratio.

**Prioritisation and hypothesis:** reduce work irrelevant to the request in the setup stage where the failure was observed. Bandwidth/KV-layout/scheduling were not experimentally excluded; no old-code initialization timer establishes descriptor construction as the dominant cause.

**Intervention and checks:** request-scoped source/destination descriptors, preserved mappings/precision/notifications,720 CPU range-equivalence cases. The geometry fixture explicitly does not validate real GPU transport.

**End-to-end evidence:** patched 22294 warmed both actual P/D paths in 0.68–0.70 s/request and full N 32 measured 1422.96 good tokens/s at 95.87%jointSLA with zero errors/cancels. There is no successful unpatched scored control, so this is patched-path feasibility, not a quantified descriptor-only end-to-end improvement. Do not divide 360 s by 0.7 s: one is a timeout.

**Next question:** once serving is feasible, inspect GPU work and request tails. SeparateN 48 profile 24819 records group GEMM 21.642%, collective / RMSNorm 23.479% and FlashInfer attention 15.064% of summed kernel duration. They motivate trials, not wall-time bottleneck percentages. Main 6–7; backups 24–25. Detailed source audit: KV_TRANSFER_REASONING_AUDIT.md.

## RQ 3 — which changes improve the actual objective?

**Hypothesis:** phase-specific implementations and load can improve qualifying service, but isolated proxy gains can be misleading.

**Matched N 60 experiment:** H 200 control 24912 and HPC-Ops decode repeat 24913 retain DeepGEMM prefill/chunk 8192 and full 60/120/30 protocol. Goodtokens/s rises 2838.853→2989.175, +5.295%; mean TTFT worsens 822.292→947.627 ms; mean ITL improves 16.579→14.934 ms. Original treatment 24738 is 2990.150791; repeat differs by−0.033%. This supports the configuration atN 60, not an exact kernel-level cause. Dedicated continuous hardware data is absent for 24913.

**Load decision:** full N 62 control 25365 toN 64 candidate 25366 yields 3011.875113→3044.489701,+1.082867%. Independent 25373 gives 3044.074628. ShortN 68 looked+2.27%, but full gain is only+0.083056%; retainN 64.

**Reject misleading alternatives:** H 200 cache+0.240921% fails the prospective 1% useful-gain rule; H 200 sparsegraphs lower capture memory but lose 0.370208% goodput; H 100 FA 3 lowers first-token wait yet loses 0.812% goodput. These are separate platform/control pairs. EAGLE integration repairs do not prevent its tested full arm from losing 2.080318%. Main 8–13; backups 26–32.

## RQ 4 — what is reproducible and what remains open?

**Repeated operating point:** historical N 64 jobs 25366/25373/25487 mean 3044.400475 good tokens/s. Later native 26766 is 3045.501509 in a separate runtime series. Same sampled GPU UUIDsets limit hardware diversity; do not pool unlike paths.

**Robustness checks:** valid legacy 26313 is lower at 2830.923547; graph/admission and harness differences do not establish one causal explanation. Same-comboN 52 H 200/H 100 ratio 1.188096805 informs one frozenN 50 prediction 2642.244; actualH 20024272 is 2601.629,error−1.5371%. It passes team±2%tolerance but lies outside an earlier incomplete sensitivity range; no universal hardware conversion.

**Acceptance limits:** official full-set model quality ≥99%reference remains unverified. Smoke 7/8 and retrieval 12/12 are small tests. Portable 27136/27145 complete GPU clients but original jobs fail postprocessing; CPU 27152 validates repaired readers only. Recovered 3055.330517 is not a successful post-repair full deployment. Main 14–18. Final 19–20 states decisions and proposed validation, not new jobs.
