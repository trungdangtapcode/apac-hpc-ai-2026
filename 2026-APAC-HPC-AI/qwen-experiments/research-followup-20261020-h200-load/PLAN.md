# Verify the N60 peak and test the next matched load

The completed H200 N58 interaction now has three passing observations at 2938.628, 2935.879 and 2937.148 good output tokens/s. Fresh auto N58 control is 2775.642. The separate N60 HPC-Ops point 24738 passes all local gates at 2990.151, with mean TTFT 947.652 ms and mean ITL 14.931 ms. This justifies an independent repetition and one bounded next load, not an unlimited concurrency sweep. See [completed evidence and assessment](../research-followup-20261020-0028/H200_RESULTS.md).

| Bundle | N | Purpose |
|---|---:|---|
| s18-auto-control-n60 | 60 | Fresh auto-decode control at the new peak's load |
| s18-hpc-repeat-n60 | 60 | Independently repeat job 24738 |
| s18-auto-control-n62 | 62 | Fresh control for the next runner comparison |
| s18-hpc-n62-profile | 62 | Test HPC-Ops at one higher load, then profile separately |

Each bundle is derived from an accepted frozen submitted payload, retaining the worker, transport, precision, benchmark, output checks and exact graph sizes. Only load/experiment metadata and the candidate's post-score profile switch change. Native checkpoint, BF16 KV, 16 H200, DeepGEMM prefill chunk8192, MNNVL and FlashInfer decode remain fixed. Scoring stays closed-loop 4000/200 and 60/120/30, with errors in the denominator. Profile traffic follows scoring and cannot be pooled into the score.

Keep at most five active H200 jobs. Compare candidate and control at the same N; compare repeated HPC N60 with prior HPC N60 and the N58 observations. Do not call a queued trial a result or substitute an auto-decode repeat for an HPC-Ops repeat. Require frozen-payload/raw-protocol/runtime/output/joint-latency gates on every completed point. A useful single-run gain needs a fresh matched repeat before promotion. Stop load expansion on no useful gain or failed acceptance; no N64 candidate is pre-authorised by this plan.

H100 remains a separate experiment and credit ledger. No official accuracy or global optimality claim, container/weight precision change, authentication, slides, scheduler automation or background Codex is part of this wave.
