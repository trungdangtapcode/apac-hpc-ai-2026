# Prefill Delayer Feasibility on the H200 Qwen Disaggregated Run

**Decision: do not spend a GPU trial on this control for the current P4+P4 / D8 setup.** The flag is implemented in the pinned SGLang build, but its triggers do not match the observed prefill-only scheduler state. Enabling it is expected to add scheduler collectives without delaying prefill or forming larger batches.

## What the pinned code actually does

The image is `/scratch/enroot-images/sglang-harbor.sqsh`, SHA-256 `b74ae77446bfedd6c5d72820b45be255cc513cf7c7c039d1bf63679c8178bfe5`. Selective source files and their hashes are in [SOURCE_MANIFEST.json](evidence/SOURCE_MANIFEST.json).

`--enable-prefill-delayer` defaults to `false`; its help text says it targets DP attention. The scheduler creates the delayer only when enabled, skips it on a decode engine, and otherwise creates one collective-backed delayer. Each scheduler pass can perform the delayer negotiation before admitting a waiting request.

The delay is conditional, not a fixed batching sleep:

- The default pass cap is **30 scheduler forward passes**, not 30 milliseconds.
- The slot trigger delays only when `max_running_requests - running_batch < max_prefill_bs`.
- The optional queue trigger requires `--prefill-delayer-queue-min-ratio` and a positive running batch. It waits until the waiting queue reaches `min(running_batch * ratio, max_prefill_bs)`.
- `--prefill-delayer-max-delay-ms` is a **millisecond** wall-clock cap for that queue trigger only; unset means 5000 ms. This is far too large to use unchanged under a 3000 ms TTFT limit, and setting a smaller cap would not fix the absent trigger in this workload.
- A low token-usage watermark can force prefill through; it is unset by default.

The implementation is in [prefill_delayer.py](evidence/sglang/srt/managers/prefill_delayer.py); defaults and option descriptions are in [server_args.py](evidence/sglang/srt/server_args.py); scheduler construction and invocation are in [scheduler.py](evidence/sglang/srt/managers/scheduler.py) and request-admission checks are in [schedule_policy.py](evidence/sglang/srt/managers/schedule_policy.py).

## Match against the actual H200 control logs

Jobs 27270 and 27376 both ran the relevant prefill workers with TP4, chunked prefill 8192, maximum prefill tokens 16384, breakable prefill graphs, `enable_dp_attention=False`, `disable_overlap_schedule=False`, `enable_prefill_delayer=False`, `prefill_delayer_queue_min_ratio=None`, and `prefill_delayer_max_delay_ms=None`. Their prefill startup logs resolve `max_running_requests=4096`.

Across the two prefill-worker logs per job, logged prefill batches have `#running-req: 0`; the batch counters show a median of 3 new sequences and a maximum of 4, while the queue counter's median is 0 (maximum 26). The queue maximum shows that arrivals can accumulate, but the delayer's queue trigger explicitly requires a positive running batch. With no running requests, the queue trigger is false. The slot trigger is also false at the observed scale: `4096 - 0 < max_prefill_bs` cannot hold for batches of at most four requests. DP attention is disabled, so the stated DP-attention idle-time use case is absent as well.

The candidate roles are disaggregated prefill workers: they process prompt chunks and hand KV state to the decode workers; they do not retain generated requests as a running decode batch. The `#running-req: 0` logs corroborate that scheduler state. Thus neither a pass-cap value nor a short millisecond cap can manufacture the missing positive running batch or a useful delayer trigger. The prior tokenizer-batching trials are a different mechanism: they combine tokenization work; this control acts at scheduler request admission and does not provide an unconditional 0.2 ms or 2 ms wait.

## Search coverage and recommendation

The selective configuration search in `serving-tuning-08` through `serving-tuning-11` found no prior prefill-delayer experiment. Existing tokenizer-batching trials in tuning 11 do not count as delayer tests.

**No finite delayer arm is recommended for this topology.** A hypothetical queue ratio and 1–10 ms cap would still have no effect because `running_batch` is zero. Raising the pass cap or turning on an unbounded queue wait would add TTFT risk without a mechanism to improve batching. Revisit only if a future architecture actually enables DP-attention prefill or logs show a positive prefill scheduler running batch and sustained small-fragment queueing. Any such trial must first establish a matched control with the exact same runtime, model, N64 workload and quality gates.

This is a source-and-observed-state feasibility conclusion, not a benchmark result. No delayer-enabled GPU run was made, and no speedup is claimed.

## Evidence references

- Job 27270 logs: [prefill worker 0](../runs/27270/prefill-0.log), [prefill worker 1](../runs/27270/prefill-1.log).
- Job 27376 logs: [prefill worker 0](../runs/27376/prefill-0.log), [prefill worker 1](../runs/27376/prefill-1.log).
- Image identity, source hashes and run-log hashes: [SOURCE_MANIFEST.json](evidence/SOURCE_MANIFEST.json).
- Bounded search: `serving-tuning-08` through `serving-tuning-11`; tuning 11 contains tokenizer-batch arms but no delayer arm.
