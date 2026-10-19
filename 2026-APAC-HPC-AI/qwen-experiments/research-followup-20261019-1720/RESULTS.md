# H100 protocol and host-profile review — 19 October 2026

All three allocations ended with exit status zero and separately passed the full local frozen-payload, protocol, error, latency, runtime, short-output and 12-case long-context checks. These checks do not establish the organiser's required full-set accuracy.

| Job | Trial | Good output tokens/s | Joint good requests | Mean TTFT (ms) | Mean ITL (ms) |
|---|---|---:|---:|---:|---:|
| 221884 | Instrumented control | 2415.474 | 98.613% | 724.471 | 18.202 |
| 221885 | Global prefill Simple | 2421.066 | 98.617% | 718.576 | 18.175 |
| 221886 | Baseline with CPU/GPU post-score profile | 2425.886 | 98.554% | 720.397 | 18.128 |

The global Simple setting is **0.2315%** above its matched instrumented control. This small single comparison does not establish a useful gain against baseline variation. It does not beat the highest H100 observation, 221590 at 2430.891 good output tokens/s. The independent baseline repeat 221886 remains below that observation and supplies CPU/GPU evidence, not a new winner.

## Protocol activation remains unresolved

Both trials use Torch NCCL 2.28.9. Candidate logs explicitly report that NCCL read `NCCL_PROTO=Simple`. Nevertheless, sealed separate N48 diagnostic traces show Ring LL and no named Simple all-reduce kernel on all eight prefill ranks. Each job has 16 nonempty rank traces and all diagnostic requests succeeded (372 control, 377 candidate). Environment parsing is now demonstrated, but activation on the measured kernel path is still unverified. This is not proof of the protocol used by every ranked N54 call. Close further full-model protocol-selector sweeps until a smaller communicator reproduction explains this discrepancy. Do not promote the 0.23% point or claim Simple caused it.

## CPU and GPU evidence

Job 221886 captures CPU operations, CUDA runtime calls, scheduler annotations and GPU kernels after scoring. `cpu-timeline-analysis.json` records all 16 ranks with seals, operation counts and kernel interval coverage. Synchronisation time is waiting, not independent CPU work; nested CPU durations and summed kernel durations cannot be treated as end-to-end bottleneck shares. This profile motivates one bounded host-overhead hypothesis, without establishing that the service is CPU limited.

The pinned SGLang `DynamicGradMode` selects `torch.no_grad` by default and can opt into inference mode through `SGLANG_ENABLE_TORCH_INFERENCE_MODE`. Both normal and overlap scheduler loops use this decorator. [PyTorch's API reference](https://docs.pytorch.org/docs/stable/generated/torch.autograd.grad_mode.inference_mode.html) explains that inference mode removes view tracking and version-counter work; that is a mechanism, not a prediction of serving speed. Test decode-only inference mode against an equally instrumented explicit-default control, preserving the same workload, precision, transport and output checks. Do not change synchronisation or memory-safety barriers.

## Credit and evidence

The 17:20 UTC scheduler check found no own active PBS allocation. Published ledger at 20/10/2026-01:00:01 SGT shows Used 32604.728 SU, Balance 31395.272 SU and In Doubt zero. The four newly terminal charges total 1875.626 SU and reconcile the published Used delta, releasing their 6144-SU maximum reservations. Internal headroom before new work is 18395.272 SU under the unchanged 51000-SU cap and 13000-SU buffer. Max reservations are bounds, not actual charges.

Raw collector receipts, sealed immutable snapshots, per-job gates/reviews, profile analyzers and selected runtime source hashes are retained beside this report. H200 still has five Priority-pending jobs at the 17:20 UTC check; do not cancel or pool platforms. Earlier submission-time queue and budget figures are historical.
