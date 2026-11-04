# Request-scoped NIXL descriptors

> Retrospective explanation from retained code, tests and run logs. No new experiment was run for this note.

## 1. What problem led to this work?

Workers in historical H200 job **22271** loaded the model and reported ready. A warmup request through both prefill and decode then hit its **360-second deadline**. AIPerf had not started scoring: the team had a service path that was not yet usable, not a low throughput score.

The branch used **TP8/EP2 prefill → TP4/EP4 decode**. This is the historical recovery branch, not the later selected two-TP4-prefill/TP8-decode recipe.

Source: [unpatched warmup log](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/runs/22271/pair-warmup.log), [retained reasoning audit](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/ai-final-report-20261030/KV_TRANSFER_REASONING_AUDIT.md).

## 2. How did the team find a concrete hypothesis?

The team inspected the SGLang NIXL integration used by the container. When attention tensor-parallel widths differ, this code must map the source KV heads and byte ranges onto the destination ranks.

In the original `_init_hetero_tp_prep_handle`, the code created a slot array across the reserved KV pool and expanded it across K/V layer pointers. That exposed a large piece of **metadata preparation** before useful request execution.

```python
# Extract from the retained original source.
num_slots = self.kv_args.kv_data_lens[0] // src_kv_item_len
slots = np.arange(num_slots, dtype=np.uint64)
```

For the representative source geometry, **2,148,119 slots × 94 layers × K/V = 403,846,372 source entries per rank**. A single request uses only its allocated pages.

A descriptor describes an address, length and device. Preparing descriptors for the whole pool does **not** mean the old code transmitted the whole KV pool. The proposed intervention reduced setup metadata, while preserving the bytes each request needed.

Source: [original source around pool enumeration](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/nixl-ondemand/original-conn.py#L858), [patch metadata and scope](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/nixl-ondemand/metadata.json).

## 3. Why investigate this before bandwidth or scheduling?

- The failure appeared during initial pair warmup, before a scored service run.
- Source inspection identified a specific setup operation that scaled with reserved pool capacity.
- A bounded change could be checked against the original byte ranges on CPU before another distributed run.

This made metadata preparation a practical first experiment. It did not establish that bandwidth, KV layout or scheduling were healthy, or that descriptor construction alone caused the timeout.

## 4. What exactly changed?

| Location | Original implementation | Patched implementation |
|---|---|---|
| `_init_hetero_tp_prep_handle` | Prepare descriptor lists covering reserved pool slots. | Store compact pointer/stride/head geometry in `_ondemand_slice_plans`. |
| `send_kvcache_slice` | Select transfers from prepared pool lists. | Construct source and destination address ranges from this request's page lists. |
| Adjacent ranges | Numerous per-token entries in the pool representation. | Coalesce contiguous runs only when source and destination bytes can safely be represented as whole-token ranges. |
| Partial KV-head slices | Preserve per-token addressing. | Still preserve per-token stride; do not merge over unrelated head bytes. |
| Model and other paths | Original checkpoint, precision, head mapping and notifications. | Retained; equal-TP transfers are outside this patch's scope. |

Source: [reviewable patch](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/nixl-ondemand/nixl-ondemand.patch), [patched preparation](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/nixl-ondemand/conn.py#L776), [patched send path](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/nixl-ondemand/conn.py#L1616).

## 5. Why is the coalescing condition important?

The implementation merges only when the transfer covers a whole source token and a whole destination token:

```python
if length == plan["src_stride"] == plan["dst_stride"]:
    boundary[1:] = (
        (src_tokens[1:] != src_tokens[:-1] + 1)
        | (dst_tokens[1:] != dst_tokens[:-1] + 1)
    )
```

**Illustration, not a measurement:** two required ranges `[0, 100)` and `[100, 200)` can become `[0, 200)`. But ranges `[0, 100)` and `[400, 500)` must remain separate. Merging them would include bytes the request did not ask to transfer. Source and destination must both be contiguous; continuity on just one side is insufficient.

## 6. How was correctness checked before using GPUs?

The CPU harness extracted the actual old and new functions, replaced the NIXL transfer calls with a recording stub, and compared the resulting source/destination byte slices and notifications.

| Coverage | Retained check |
|---|---|
| Attention TP | 2, 4 and 8; heterogeneous directions and relevant ranks. |
| KV heads | 4 and 8. |
| Page size | 1, 4 and 16. |
| Request pages | Contiguous, noncontiguous and single-page patterns. |
| Equivalence cases | **720 passed**. |
| Full-size geometry example | 94 layers, 4,000 contiguous prompt tokens, TP8→TP4: **188 request descriptors**. |

The 188 entries correspond to one coalesced range for each K/V layer in that example. The 403.8-million and 188 counts describe different scopes; they are not an inference speedup ratio.

Source: [CPU test harness](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/test-nixl-ondemand.py), [recorded geometry result](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/nixl-ondemand/geometry-test.json).

## 7. What happened on the real serving path?

| Observation | Before: 22271 | Patched: 22294 |
|---|---|---|
| Worker model load | Ready. | Ready. |
| Pair warmup | Deadline expired at 360 seconds. | Both tested P/D routes completed, about 0.68–0.70 seconds/request after readiness. |
| Full benchmark | Not reached; no score. | Full N32 confirmation completed. |
| Good output throughput | No scored result. | **1,422.96 good output tokens/s**. |
| Joint latency pass share | No scored result. | **95.87%**. |
| Scored errors / cancellations | No scored result. | **0 / 0**. |

The team kept the change because the patched branch completed real requests and a full benchmark. The CPU checks established intended range equivalence in tested geometries; the GPU run supplied the separate end-to-end execution evidence.

Source: [patched warmup log](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/runs/22294/pair-warmup.log), [recovery measurements](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/RECOVERY_RESULTS.md).

## 8. What can this result establish?

- **Established:** a bounded integration change, 720 CPU equivalence cases, and a usable patched P/D branch with a scored run.
- **Not measured:** isolated old-versus-new descriptor setup time or a descriptor-only throughput gain. There was no successful unpatched scored control for this branch.
- **Do not infer:** 360 seconds versus 0.7 seconds is a setup speedup, the descriptor counts are a bandwidth ratio, or this intervention independently explains the final approximately 3,052-token/s recipe.

This was a compatibility and service-recovery contribution. Later backend and concurrency improvements have their own controlled comparisons.
