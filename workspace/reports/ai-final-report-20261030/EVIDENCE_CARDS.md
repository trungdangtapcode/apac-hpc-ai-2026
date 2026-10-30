# Evidence behind the engineering investigation

Use [the classified contribution stories](investigation-contributions.json) for problem, prioritisation, hypothesis, change/control, evidence, decision and limit. Use [mock panel Q&A](MOCK_QA_EVIDENCE.md) for short spoken answers and exact retained source links. This is preparation, not a claim that a mock interview has occurred.

| Story | Claim class | Main slides | Detailed backups |
|---|---|---|---|
| Choose a usable 16-H 200 split | Engineering decision | 3–4 | 17–19, 26 |
| Make heterogeneous-TP KV setup request-scoped | Team implementation; patched-path feasibility | 5–7 | 20–21 |
| Test integrated backend and load choices | Experimental method and findings using provided kernels | 8–12 | 22–25, 27–28, 30, 32 |
| Bound robustness, quality and deployment claims | Evidence limits and proposed validation | 13–16 | 29, 31 |

## The three strongest evidence points

**KV recovery:** 22271's ready workers failed pair warmup at 360 seconds, with no scored benchmark. Source inspection and 720 CPU range checks support a request-scoped mapping change. Patched 22294 completes real warmup at 0.68–0.70 seconds/request and fullN 32 at 1422.96 good tokens/s,95.87%joint success,zero errors. This proves patched-path feasibility in that run, not descriptor-only end-to-end speedup: the unpatched scored control and isolated setup timer are missing. The 403.8 million versus 188 counts have different scopes. [Detailed audit](KV_TRANSFER_REASONING_AUDIT.md).

**Full N 60 implementation pair:** 24912 AUTO decode control versus 24913 HPC-Ops decode repeat holds the stated topology/workload/prefill settings. Good output tokens/s rises 2838.853→2989.175,+5.295%; TTFT worsens 822.292→947.627 ms; ITL improves 16.579→14.934 ms. The candidate repeat is 0.033% below original treatment 24738. This supports the tested integrated configuration, not a universal kernel advantage or exclusive causal mechanism. N 48 profiling is a separate diagnostic; dedicated continuous hardware sampling for 24913 is absent.

**Load selection:** fullN 62→N 64 gains 1.082867%, and independent 25373 differs from 25366 by−0.013634%. A shortN 68 signal of+2.27% shrinks to+0.083056% in its full comparison. KeepN 64 rather than extrapolate that concurrency always helps. Client concurrency is not the instantaneous decode batch size; queue-versus-compute timing is not isolated.

## Do not flatten different evidence classes

HistoricalN 64 jobs 25366/25373/25487 mean 3044.400475. Native 26766 at 3045.501509 is a separate runtime series; original portable 27145 recovered raw 3055.330517 is inside a FAILED job. Cache 27378 at 3048.446289 is only+0.240921% over its own fresh 27376 control and is not a confirmed replacement. The lower valid 26313 result remains unexplained, not erased. Full-set quality≥99%reference is unverified; smoke/retrieval are small checks. See the exact run references in the Q&A.
