# Four H200 verification measurements complete: retain the existing recipe

The owner's question was how to compare settings selected on different GPUs.
The final answer uses a fresh same-H200 control and transferred alternatives,
rather than multiplying H100 performance by an assumed hardware ratio. All four
allocations use 16 H200 on g1/g4, and all complete 0:0 with independent full local
raw workload, source/runtime, physical KV, semantic and output gates passed.

| Job | Change and control | Good output tokens/s | Assessment |
|---|---|---:|---|
| 27777 | Fresh H200 DeepGEMM/chunk 8192 prefill, FlashInfer decode, N64 |3038.022907| Current matched control |
| 27779 | Only decode attention changed to FA3, N64 |2999.245473| -1.276404%; reject this arm |
| 27781 | H100 both-HPC-Ops/chunk 4096 recipe at N54 |2738.940099| Useful load comparison; not same-load control |
| 27783 | Same H100 recipe at N64 |2721.815800| -10.408319% versus 27777; reject this port |

27783 closes the prior same-load evidence gap. It retains both HPC-Ops phases,
chunk 4096, two TP4/EP1 prefills and one TP8/EP8 decoder; the comparison changes the
prefill runner and chunk together. Native dependent prefill graph range and
speculative-runner fallback fields follow those choices; no draft is loaded.
The exact argument audit permits only these declared dependencies and generated
engine seeds. Decode arguments differ only by seed between 27777/27783. Thus the
result selects a serving package; it does not isolate a runner or chunk effect.

For the H100 recipe alone, N54 to N64 changes goodput -0.625216%, TTFT mean 896.156
to 1591.493 ms and p95 1106.815 to 2017.559 ms, while mean ITL 14.868 to 14.872 ms is
nearly unchanged. Prefill queue means rise 1.5417/1.2083 to 7.3750/4.4583 requests;
decode running means grow only 42.4583 to 44.1667. These observations support a
waiting-work interpretation, but no direct queue/compute/transfer decomposition
was collected, so do not attribute the extra 695 ms to a specific kernel or claim
proof of its causal share. Larger closed-loop concurrency is not an arrival rate.

27783 has 1689/1717 good (98.369249%), 28 TTFT/0 ITL breaches, zero scored errors or
cancellations, smoke 7/8 non-regression and retrieval 12/12. No selected transport/
OOM error marker or Python traceback in the three role logs. 72 metric polls all
return 200. 24 five-second samples per role cover 16 distinct GPU UUIDs: decode mean
activity 100%, VRAM 130.631 GiB/GPU, running mean/max 44.1667/47, queue max 0 and KV
token occupancy mean 0.1196. Prefill activity means 94.635%/91.719% and sampled
queue maxima 10/8. Power/clocks/temperature/CPU observations are retained and
inspected; sparse sampling, uncalibrated host clocks, missing heavy/per-thread/
Xid/throttle profiles and actual generated token IDs limit interpretation.

Decision: keep the existing H200 DeepGEMM/chunk 8192 prefill and HPC-Ops/
FlashInfer/MNNVL decode at N64. The H100-selected recipe is not the best H200
choice among these measured alternatives. H100 remains valuable for screening
compatibility, mechanisms and hypotheses; final platform selection needs native
same-hardware measurements. No universal GPU multiplier or global optimum claim.

All four retain the fixed full 60/120/30 and requested 4000/200 seed 2026 workload.
Full official model accuracy remains UNKNOWN; small smoke/retrieval checks are
not 99%-reference certification. The historical H200 mean 3044.400475 remains a
separate retained series; fresh 27777 is the comparison denominator for this wave.

The wave uses 12.671111 actual GPU-hours versus 18.133334 maximum, zero PBS SU.
All raw files and frozen payloads are sealed, with recovery manifests and safe
Git capture. Large external bytes require a separate off-host copy. The requested
four-job wave is complete; no losing repeat, blind fifth job, broader restart,
H100 authentication/spending, HPC edit, schedules or background Codex is implied.
The working final report gains this result; published PPTX/ZIP remain unchanged.

[Final source-backed comparison](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-h100-transfer-review-20261031/FINAL_RESULTS.md),
[runtime and accounting audit](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-h100-transfer-review-20261031/final-comparison.json).
