# Separate the phase affected by inference mode

The queued pair 221923 → 221924 compares explicit no_grad on both phases with decode-only inference mode. While it waits for exclusive nodes, use the remaining third slot for the independent **prefill-only** treatment against the same matched control 221923. This changes the phase being tested, not the ranked workload or the load. No losing candidate is being repeated, and no gain is predicted.

Job 221886's sealed CPU/GPU profiles contain copy, contiguous and view-related operations in prefill as well as decode; decode kernel coverage is approximately 95.5–95.7% during its profiled interval. Neither observation proves a host bottleneck. Some CPU durations include waiting and nested work; prefill replica intervals differ. Testing decode alone therefore cannot answer whether the supported host-overhead option behaves differently in prefill. The [PyTorch mechanism](https://docs.pytorch.org/docs/stable/generated/torch.autograd.grad_mode.inference_mode.html) is reduced view/version tracking. The exact pinned SGLang scheduler uses DynamicGradMode on both event loops, with source hashes and a context check already in the matched control payload.

| Trial | Prefill mode | Decode mode | Role |
|---|---|---|---|
| 221923, already queued | no_grad | no_grad | Shared instrumented control |
| 221924, already queued | no_grad | inference_mode | Decode-only candidate |
| New candidate 51 | inference_mode | no_grad | Prefill-only candidate |

Worker 51 differs from the shared control in one environment value before server import. Source-hash/context preflight, model settings, BF16 key/value cache, native weight precision, both-phase HPC-Ops, chunk4096, exact decode graphs, MNNVL transport, fixed N54 scoring, short/long output checks and the separate CPU/GPU post-score profile are identical. Do not infer how combining both phases performs from two independent tests; a combined test would require evidence first.

Submit afterany:221924 to retain one running 16-GPU allocation and at most three active PBS jobs. Reserve at most 1536 additional SU (45 minutes); total maximum reserve becomes 4608 SU and internal headroom 13787.272 SU if the ledger remains unchanged. Keep the 51000-SU cap and 13000-SU project buffer. Recheck actual queue/credit before qsub. Preserve all existing H200 queue positions.

Accept only after actual context activation, frozen payload, runtime, error, latency and output gates pass. Compare each candidate with 221923, not with the other phase candidate alone. Repeat a useful gain with a fresh matched control before promotion. If neither phase shows a useful benefit, close this option and move to source-supported communication or MoE kernel work. No new precision, request shortcuts, synchronisation-barrier changes or official accuracy claims.

The [NCCL correction](../status-review-20261019-1755/CORRECTION.md) was resolved from retained source/logs without spending GPU credit. A new GPU job solely to explain LL-labelled symbols is unnecessary.
