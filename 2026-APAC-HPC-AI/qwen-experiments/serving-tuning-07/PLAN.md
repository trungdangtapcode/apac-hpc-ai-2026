# Profile-guided decode experiments

Updated 2026-10-15. All scripts and submission notes are in English. Qwen track only.

## Measured position

Round-robin N52 now has three independent measurements: 2402.64 (23325),
2397.72 (23576), and 2400.02 (23607) good output tokens/s, each approximately
98.93% SLA. N53 reached **2433.41 good tokens/s, 98.88% SLA** (23616), the highest
observed passing N53 point at that time. Its independent repeat **23773** completed
at **2438.47 good tokens/s, 98.88% SLA**, with zero errors/cancellations. The N53
gain is now reproduced at this topology. N54 passed SLA but fell to2358.64.

The round-robin backend experiments completed, with zero errors/cancellations:

| Job | Backend change | Good tokens/s | SLA | Decision |
|---|---|---:|---:|---|
| 23608 | FP8 E4M3 KV on both roles | 254.47 | 10.75% | Reject at N52: mean ITL20.069ms crosses the20ms gate |
| 23609 | Decode DeepGEMM MoE | 2021.39 | 84.71% | Reject at N52: below90% SLA |

These are completed measurements that **failed the latency requirement**.
Their raw output rates were2368.03 and2386.12 tokens/s respectively; raw speed
does not compensate for request latency failures. Neither triggered an automatic
repeat or a higher-load job. Eight-case output diagnostics matched the known
baseline failure pattern; organiser full-set accuracy remains unverified.

## New evidence and hypotheses

Job23607 captured all16 GPU rank traces after its official benchmark, using
separate52-request diagnostic traffic. The retained summary is
[kernel-summary.json](../runs/23607/diagnostic-profile/kernel-summary.json).
Representative decode TP0 summed GPU kernel durations included27.40% MoE,
20.06% collectives, and19.64% in the main BF16 FA3 attention kernel.
These fractions are **not wall-clock shares or predicted speedups**.

Three independent N52 tests use the frozen round-robin bundle from23576:

| Job | Trial | Only change |
|---|---|---|
| 23776 | CUTLASS MoE | Decode `--moe-runner-backend cutlass` |
| 23777 | FlashInfer attention | Decode `--decode-attention-backend flashinfer` |
| 23778 | MNNVL collective | Decode `--flashinfer-allreduce-fusion-backend mnnvl` |

CUTLASS targets the grouped block-FP8 expert GEMMs. The actual staged source
has an SM90 path for this quantization, separate from its SM100-only MXFP8 path.
FlashInfer targets the decode attention work while keeping prefill FA3, BF16 KV,
page size and NIXL geometry unchanged. The staged collective resolver explicitly
allows MNNVL on SM90 within one node; decode TP8 is entirely on one node even
though the full P/D deployment occupies two nodes. This compares an alternative
fused allreduce implementation with the profiled TRTLLM path.

The exact staged source snapshots and hashes are in [inspection](inspection/).
These are compatibility checks from source; successful GPU startup and the
effective backend still need checking in each run's logs. A backend that silently
falls back must be reported as such before attributing a gain to its kernel.

All tests retain16 H200, P8-TP4_D8-TP8-EP8, BF16 KV, all model experts, official
FP8 checkpoint, chunk4096, dense decode graphs1–64, round-robin prefill routing,
request-scoped NIXL patch, and the unmodified benchmark/client. No below-FP8
format or quantized communication is enabled. Every scored point uses
60s warmup /120s measurement /30s grace,4000 input /200 output tokens.

## Queue and decision policy

The original N53 repeat keeps its queue position. The initial controller limit
was four pending/running jobs. On2026-10-15, public Slurm QoS inspection confirmed
the actual per-user pending/running limit is five; active wave7 plans were amended
to five, sharing that cap with the new DP-attention pilot23780. The45-second
controller keeps progressing without another user prompt.

For each measured backend, require a full passing N52 point with no errors or
cancellations and the same-attempt output research gate. A gain of at least2%
over both the original N52 reference and the fresh23607 N52 control triggers
one independent N52 repeat. Only a repeat that preserves that gain, SLA≥95%
and mean ITL≤19.3ms triggers N54. This bounded wave permits at most nine
deployments: three initial tests and up to two dependent tests per candidate,
apart from explicitly recorded budget retries. Failures without exports remain
incomplete, and never count as a measured load boundary.

The current N53 best must also be beaten before selecting a new performance
winner. Full organiser accuracy is required before contest promotion; a fast
benchmark or an eight-case smoke diagnostic cannot establish the99% gate.
The submission package is not automatically replaced by experimental results.

## Evidence review, 2026-10-15 15:47 UTC

Job23777 completed the full N52 protocol at2440.386061375686 good tokens/s,
98.9474% SLA, mean ITL18.7133ms and TTFT438.0483ms;1520 requests and zero
errors/cancellations. All eight decode ranks explicitly log the hybrid backend
`decode_backend=flashinfer, prefill_backend=fa3`. Output diagnostics remain7/8,
with only the independently known reverse-string failure and no new failure.
This is research eligibility, not organiser accuracy. Its gain is about1.68%
over23607 and only0.08% over repeated N53 job23773.

The existing automatic2% repeat gate remains unchanged and was not met. No N54
or exceptional repeat is submitted in this review. An independent FlashInfer
repeat remains a possible explicitly recorded plan extension after the NSCC
baseline is ready; a single near-tie cannot select a performance winner.

Job23776 failed before benchmark export. Its first retained traceback reports
illegal memory access during decode CUDA graph capture, through
`fp8.py:2417 -> cutlass_fused_experts_fp8 -> cutlass_moe.py:335`, at the call to
`apply_shuffle_mul_sum`. CUDA errors are asynchronous, so the final Python frame
does not identify the faulty kernel. Keep it INCOMPLETE, not a measured SLA/load
failure. No speculative configuration repair or resubmission was made.

Jobs23778 and23780 were still PENDING in live Slurm at15:46UTC; their registry
ACTIVE state does not imply execution. [Review evidence](inspection/review-20261015-1542UTC.json).

Primary references: [SGLang attention backends](https://docs.sglang.io/docs/advanced_features/attention_backend),
[SGLang expert parallelism and MoE runners](https://docs.sglang.io/docs/advanced_features/expert_parallelism).
The inspected image source takes precedence over newer documentation.

- [Prepared jobs](prepared-pilots.json)
- [Automatic follow-up decisions](followup-plan.json)
- [CPU payload and CLI validation](cpu-validation.json)
- [Queue validation](controller-validation.json)
- [Follow-up validation](followup-validation.json)
- [Live measurements](../SERVING_TUNING_RESULTS.md)

## Startup review, 2026-10-15 16:03 UTC

Live Slurm confirms23778 started at16:01:05UTC on g1/g4. All eight decode
ranks log `FlashInfer AllReduce Fusion enabled and workspace initialized:
backend=mnnvl` at16:02:43UTC. This is runtime backend-initialization evidence,
not a passing request or performance measurement; the inspected log is still
in decode CUDA graph capture. No benchmark export or output diagnostic is
available yet.23780 remains PENDING(Resources). The existing watcher retains
its lock and owns result collection and the unchanged2% follow-up gate.
[Timestamped startup snapshot](../nscc-pbs/inspection/wake-20261015-1600UTC/wake-summary.json).

## Completed MNNVL review, 2026-10-15 16:32 UTC

Slurm23778 completed at16:09:58UTC with exit0. Its full N52 export records
2592.162388904698 good tokens/s,99.0068% SLA (1595/1611 requests), mean
ITL17.1273ms, mean TTFT516.2843ms, and zero errors/cancellations. The export
configuration confirms60s warmup /120s measurement /30s grace. All eight decode
ranks initialized MNNVL; this is not a new kernel profile or a kernel-time claim.

Goodput is8.01% above fresh N52 control23607 and7.89% above original23325;
it is6.30% above repeated N53 job23773. Mean ITL falls2.40ms versus23607,
but mean TTFT rises169.44ms. Preserve this tradeoff when assessing the result.
The same-attempt output diagnostic remains7/8 with only the known reverse
failure, so research is eligible while organiser accuracy remains unverified.

The unchanged automatic2% gate correctly triggered independent N52 repeat
23839 at16:11:17UTC. At this review, live Slurm reports both23839 and23780
PENDING(Priority). Repeat configuration differs only in experiment name/purpose;
worker, client, topology launcher and smoke diagnostic match byte-for-byte.
N54 remains gated on a reproduced gain, SLA>=95% and mean ITL<=19.3ms.
No additional job or exceptional repeat was submitted in this wake.
[Independent export and payload review](../nscc-pbs/inspection/wake-20261015-1630UTC/mnnvl-review.json).

## Independent repeat completed — 2026-10-15 21:01 UTC

23839 completed exit0 at20:59:45UTC,2592.92goodtokens/s,99.0074%SLA,
ITL17.1545ms,0errors/cancel; same-attempt7/8 with no new failed cases.
Two-run mean with23778 is2592.54, gain8.02% over23607 and6.32% over23773.
The unchanged gate triggered N54 job23924 from the existing watcher at21:00:05;
live21:01:24UTC confirms PENDING(Priority). This replaces earlier pending-only
snapshots, which remain historical. All sealed checksums and matched payloads
passed independent review. [Detailed comparison and N54 review step](MNNVL_REPEAT_REVIEW.md).
