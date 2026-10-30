# KV descriptor claim: evidence and limits

This audit addresses the slide claim that a representative heterogeneous-TP NIXL source descriptor list fell from about 403.8 million pool entries per rank to 188 coalesced entries for a contiguous 4,000-token request. The quantities count transfer descriptors; they are not bytes, transfer bandwidth, or a measured speedup.

## What symptom prompted the change

During topology recovery, several disaggregated prefill/decode workers became ready but the client could not complete pair warmup. In the relevant P8-TP8/EP2 prefill to D8-TP4/EP4 decode branch, job 22271 loaded the model but its pair-warmup request timed out after 360 seconds and produced no benchmark. Its retained `pair-warmup.log` ends in an HTTP `TimeoutError`; the contemporaneous [topology review](../../../2026-APAC-HPC-AI/qwen-experiments/TOPOLOGY_REVIEW.md) explicitly says the bootstrap/transfer path was not yet proven. Job 22294 repeated that topology with the descriptor patch; its pair warmup completed both P/D paths in 0.68–0.70 seconds per request after workers were ready.

The symptom was therefore a cold P/D bootstrap or transfer warmup that did not finish, not an observed steady-state network saturation or a measured slow KV copy. Other topology failures had distinct causes (including FP8 shard incompatibility and a port collision), so those are not evidence for this patch.

## Affected component and why it was investigated

The affected code was SGLang's NIXL heterogeneous-tensor-parallel KV descriptor preparation and transfer path: prefill and decode use different attention-TP sizes, so this path maps source KV heads and byte ranges onto decode peer ranges. The patch metadata says its scope is only heterogeneous-TP KV descriptor preparation/transfer; equal-TP transfers, weights, precision, head mapping, and notifications were retained. The [patch](../../../2026-APAC-HPC-AI/qwen-experiments/nixl-ondemand/nixl-ondemand.patch) replaces full-pool source/destination descriptor enumeration with per-request descriptors and coalesces contiguous ranges while preserving per-token stride when only a KV-head slice is sent.

The source-backed cost signal was large: the retained [NIXL note](../../../2026-APAC-HPC-AI/qwen-experiments/nixl-ondemand/README.md) derives approximately 403.8 million source descriptors per rank from 2,148,119 KV slots, 94 layers, and K/V entries, for the representative TP8 source geometry. For a contiguous 4,000-token TP8→TP4 request, the CPU geometry check reports 188 descriptors. This made descriptor construction a plausible startup hypothesis worth testing. Because the symptom occurred before successful scoring and the proposed change targeted setup work, descriptors were a more directly evidenced target than steady-state bandwidth, KV layout, or scheduler placement. This is a prioritization rationale, not proof that those alternatives were ruled out.

The retained [geometry result](../../../2026-APAC-HPC-AI/qwen-experiments/nixl-ondemand/geometry-test.json) passes 720 original-vs-patched byte-range equivalence cases and records 188 descriptors, but explicitly marks real GPU transport validation false. This establishes address/range equivalence in tested CPU cases, not that descriptor creation alone caused the timeout.

## End-to-end evidence

- **Before patch:** job 22271: model workers loaded; pair warmup timed out at 360 seconds; no benchmark/export and no throughput result.
- **After patch:** job 22294: both actual P/D warmup paths completed in 0.68–0.70 seconds per request once servers were ready. Its full N32 confirmation scored 1,422.96 good output tokens/s at 95.87% joint SLA, with zero errors and cancellations. This is an end-to-end feasibility result for the patched P8-TP8/EP2 → D8-TP4/EP4 configuration.
- **Not measured:** there is no successful no-patch end-to-end control for this exact topology, no separately timed old-vs-new descriptor initialization, and no controlled latency decomposition attributing the warmup change to descriptor work rather than other run differences. Thus the evidence does not quantify a pre/post speedup or prove descriptor enumeration was the sole cause. Nor does the 1,422.96 score isolate a serving-throughput effect of the patch; the layout itself differed from the earlier best topology.

## Claims supported vs unknown

1. **Supported:** the original heterogeneous-TP code enumerated descriptors across the KV pool; the patched code builds request-scoped descriptors. Retained range checks show equivalence for 720 tested CPU geometries, and the 4,000-token contiguous example uses 188 descriptors.
2. **Supported, narrowly:** the patched topology completed real P/D warmup and a full N32 benchmark where the prior 22271 attempt had timed out before benchmarking. This shows patched-path feasibility in that run, not a controlled causal attribution.
3. **Supported as motivation, not diagnosis:** hundreds of millions of descriptors per source rank were a substantial source-level setup-work signal aligned with a cold-warmup failure. No old-code initialization-time measurement establishes that this was the dominant bottleneck.

**Unknown:** exact old-vs-new setup-time reduction; how much of the timeout was descriptor construction versus other bootstrap/transfer work; network bandwidth utilization; a benefit over an otherwise identical unpatched deployment; and the patch's independent contribution to the measured goodput. Do not describe 403.8M→188 as a 2-million-fold inference speedup or as evidence that bandwidth/KV layout/scheduler causes were experimentally excluded.

## Retained source records

- `qwen-experiments/nixl-ondemand/README.md`, `geometry-test.json`, `nixl-ondemand.patch`, `metadata.json`
- `qwen-experiments/runs/22271/pair-warmup.log`, `runs/22294/pair-warmup.log`, `runs/22294/confirm/n32/artifacts/profile_export_aiperf.json`
- `qwen-experiments/RUNS.md` entries for 22271, 22294, and the later selected 22415 deployment
- `qwen-experiments/TOPOLOGY_REVIEW.md` and `RECOVERY_RESULTS.md`
