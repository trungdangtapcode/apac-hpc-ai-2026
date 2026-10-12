# TripleU APAC2026 — slide guide

Data snapshot: 2026-10-12T11:17:26.130353+00:00

English slides and speaker notes. Suggested duration: 15–20 minutes for the main 18 slides. Appendix is for Q&A.

## 01. Serving the full model. Meeting the latency gate.

- Qwen3-235B-A22B / PD disaggregated inference
- VNUHCM - TripleU
- Evidence snapshot  |  12 October 2026
- BEST INTERNAL RESULT
- 1,912.30
- good output tokens/s / 97.44% SLA fraction / N48 / 16 H200

**Speaker notes:** Our declared Qwen Basic result serves the official FP8 checkpoint on 16 H200 GPUs with plain prefill/decode disaggregation. The winning measured configuration is P8-TP4_D8-TP8-EP8 at N48, with our request-scoped NIXL descriptor patch. It achieves 1912.30 good output tokens/s and 97.44% SLA. These are local measurements, not an official organiser score.

## 02. Best measured stack, with explicit limits

- GOOD OUTPUT RATE
- 1,912.30
- req/s goodput × 200 / 9.56150 good req/s
- REQUESTS WITHIN BOTH SLAs
- 97.44%
- 1,180 / 1,211 requests / 0 errors; 0 cancellations
- VALIDATION STATUS
- Pending
- Full-set accuracy / Organiser official re-run

**Speaker notes:** Job 22415 used the long 60/120/30 protocol. Of 1211 profiling requests, 1180 met both latency limits; there were no request errors or cancellations. The primary packaged Slurm job now deploys this exact layout and patch, then runs the official client once at N48. Full-set accuracy and official organiser re-verification are pending.

## 03. Throughput counts only when latency passes

- WORKLOAD
- 4,000 → 200
- Synthetic Shakespeare inputs / Official FP8 checkpoint
- PER-REQUEST SLA
- 3,000 / 20
- TTFT ≤ 3,000 ms / Mean ITL ≤ 20 ms
- POINT ACCEPTANCE
- ≥ 90%
- Requests must pass both / Errors stay in denominator
- Closed-loop load: a completed request is immediately replaced, sustaining N concurrent requests.

**Speaker notes:** TTFT measures the wait for the first token. The per-request average ITL measures the time between output tokens. A good request must meet both TTFT at most 3000 ms and mean ITL at most 20 ms. At least 90% must pass; errors remain in the denominator. The synthetic Shakespeare performance workload is distinct from full-set model accuracy checks.

## 04. One platform, one unchanged checkpoint

- COMPUTE
- 2 × HGX H200 nodes / 16 GPUs total
- NETWORK
- InfiniBand NDR between the two nodes
- MODEL
- Qwen3-235B-A22B-Instruct-2507-FP8
- SERVING
- SGLang 0.5.17 / router 0.3.2 / NIXL 1.3.2
- CLIENT
- AIPerf 0.12.0; pinned official tokenizer
- PRECISION
- Published FP8 weights / BF16 KV (auto, verified in logs)

**Speaker notes:** The platform is two eight-GPU H200 nodes connected by InfiniBand. We reuse the exact organiser SGLang and AIPerf images. SGLang is version 0.5.17, the router 0.3.2, NIXL 1.3.2 and AIPerf 0.12.0. The published FP8 weights are unchanged; worker logs confirm BF16 KV. The included module is a read-only serving-source overlay, not a rebuilt or requantised model.

## 05. Best layout: 2 prefill + 1 decode worker

- NODE 0  /  8 H200
- NODE 1  /  8 H200
- Prefill worker 0  ·  4 GPUs  ·  TP4 / EP1
- Prefill worker 1  ·  4 GPUs  ·  TP4 / EP1
- Decode worker 0 / 8 GPUs  ·  TP8 / EP8
- KV cache / NIXL →
- AIPerf N48 → OpenAI-compatible gateway :8000 → Prefill → Decode → streamed tokens

**Speaker notes:** Node 0 has two prefill workers, each TP4/EP1 using four GPUs. Node 1 has one decode worker, TP8/EP8 using eight GPUs. NIXL transfers KV across the two possible P/D pairs. All scored requests target the OpenAI-compatible gateway, rather than worker endpoints. No tensor-parallel group spans both nodes.

## 06. Starting layouts establish our measured reference

- Reference layout 07
- Prefill: 4 workers × TP2 / Decode: 2 workers × TP4 / EP4 / Node split: 8 + 8 GPUs / Long run: N32
- Previous best layout 09
- Prefill: 2 workers × TP4 / Decode: 2 workers × TP4 / EP4 / Node split: 8 + 8 GPUs / Long run: N40
- Trade-off: fewer prefill replicas, wider tensor parallelism; measure the balance under the SLA.

**Speaker notes:** Layouts 07 and 09 are organiser-provided starting examples, not libraries or models created by our team. Layout 07 uses four TP2 prefill workers; 09 uses two TP4 prefill workers. Both use two TP4/EP4 decode workers. The previous best was 09/N40. We extend the topology search, select load and patch KV descriptor preparation. The improvement does not isolate one variable.

## 07. A 17-layout search, with measured coverage

- GPU SPLIT P + D
- PREFILL TP
- DECODE TP
- LAYOUTS
- 8 + 8
- 2 / 4 / 8
- 2 / 4 / 8
- 9
- 4 + 12
- 2 / 4
- 2 / 4
- 4
- 12 + 4
- 2 / 4
- 2 / 4
- 4
- 14/17 originals measured
- + 3 measured EP2 variants
- Each completed topology has N16, N32, N40 and N48 actual measurement exports.

**Speaker notes:** The finite search contains 17 topology arrangements across 8+8, 4+12 and 12+4 GPU splits, with compatible TP2/4/8 values. Fourteen exact originals and three explicit EP2 replacements have all four measured sweep points. Three TP8/EP1 originals remain FP8-block-incompatible. Replacements are named separately; failed deployments never count as measurements.

## 08. Screen quickly; confirm at the full duration

- Deploy + initialize
- All P/D paths / Separate setup prompts
- Explore
- N16 / 32 / 40 / 48 / 10s + 20s + 30s
- Long confirmation
- Best N48 / latest N32 / 60s + 120s + 30s
- Official timing
- 60s warmup
- 120s measurement
- 30s grace
- A short sweep and a long confirmation use different windows; their difference is not an optimisation gain.

**Speaker notes:** Exploratory runs use 10-second warmup, 20-second measurement and 30-second grace. They screen configurations and are not official scoring runs. Long confirmation uses 60/120/30. The declared entry performs only the official N48 point, without a sweep. Separate setup prompts initialize every P/D path without using the official dataset or seed and without changing official warmup.

## 09. Winner sweeps select N48; the long run confirms it

- N48 sweep: 1,788.65 good tokens/s; 90.95% SLA. Long N48: 1,912.30; 97.44% SLA.

**Speaker notes:** All four winning-layout sweeps passed the 90% gate. Short N48 produced 1788.65 good tokens/s with 90.95% SLA. The long N48 confirmation produced 1912.30 with 97.44%. These windows have different durations and populations; their difference is not an optimisation speedup. We select the long confirmation as the declared performance evidence.

## 10. Best long run: +14.78% over the previous best

- Observed gain includes topology, concurrency and transport changes. Repeated matched A/B is still needed.

**Speaker notes:** The winning long run is 14.78% above the previous long result of 1666.01. All bars show passing long measurements on the same 16-H200 platform. Topology, concurrency and transport differ, so this is an observed end-to-end gain, not an isolated NIXL patch speedup. Repeated matched A/B testing remains useful. The baseline is our local run, not the organisers reference score.

## 11. Check the gate per request, not from averages

- 1,180 / 1,211
- requests pass both limits
- Mean TTFT: 1,482.22 ms / Mean ITL: 16.79 ms / P95 TTFT: 2,456.56 ms / P95 ITL: 17.99 ms

**Speaker notes:** The original JSONL contains 1211 profiling records. Recomputing both per-request limits gives 1180 good requests, exactly matching the 97.44% aggregate fraction. Thirty-one miss a limit; none error or cancel. Aggregate means alone cannot determine whether 90% pass. The displayed TTFT and ITL statistics are performance metrics, not accuracy scores.

## 12. Failures remain evidence; actual exports count

- FP8 sharding
- TP8 / EP1 gives a 192-wide expert shard; FP8 block size is 128.
- Use a distinct EP2 variant; keep the EP1 original incompatible.
- Cold P/D transfer
- 22778 timed out before measurement; patched 22809 completes.
- Request-scoped descriptors; setup deadlines do not relax benchmark SLAs.
- Distributed ports
- A deployment hit EADDRINUSE before producing metrics.
- Assign explicit distinct ports; preserve the failed logs and source.

**Speaker notes:** Failures expose three practical issues: FP8 expert shard dimensions, slow cold KV path setup, and distributed port collisions. Job 22778 failed before measurement and is not counted as finished. The repaired equal-TP job 22809 has four sweep exports and a long N32 confirmation. A successful repaired run does not prove that a single suspected cause explained every earlier timeout.

## 13. EP2 makes TP8 compatible with FP8 blocks

- TP8 / EP1
- 128 experts / 1 expert group / 1536 ÷ 8 = 192 / 192 is not divisible by 128
- TP8 / EP2
- 64 experts / group × 2 groups / 1536 ÷ 4 = 384 / 384 = 3 × 128
- All 3 EP2 replacements are measured. All experts and weights are retained; the originals stay labelled.

**Speaker notes:** TP partitions matrices inside each expert; EP distributes expert groups. With TP8/EP1, the 1536-wide dimension produces a 192-wide shard, incompatible with 128-wide FP8 blocks. EP2 gives effective TP4 and 384-wide shards, exactly three blocks, while retaining all 128 experts and weights. These are explicit variants. The winning layout uses prefill TP4/EP1 and decode TP8/EP8.

## 14. NIXL: two request-scoped transport patches

- Full-pool descriptor plan
- ≈ 403.8 million source entries / rank
- Request-scoped plan
- 188 entries: contiguous TP8→TP4 or TP8→TP8
- Byte ranges, head mapping and notifications retained.
- 720 + 936
- CPU range cases / Both patches GPU-tested
- 1,507.96
- latest equal-TP / N32 / 95.38% SLA; no errors

**Speaker notes:** We patch SGLang integration with NIXL, not the underlying NIXL library. The heterogeneous-TP patch passed 720 CPU byte-range comparisons and is used by winning job 22415. The separate restricted equal-TP8 patch passed 936 range cases and five fallback guards; job 22809 confirms GPU operation. For contiguous TP8-to-TP4 or TP8-to-TP8 copies, 4000 tokens need 188 descriptors. This count is not universal for TP4-to-TP8 geometry. Geometry checks do not replace model accuracy.

## 15. The primary job deploys the winning stack

- 01
- Winning layout
- 2 prefill TP4 / EP1 + 1 decode TP8 / EP8; N48; all 16 H200.
- 02
- Enabled patch
- Read-only NIXL module mount; source hash checked by every worker.
- 03
- One Slurm job
- Deploy, initialize both P/D paths, run the locked official command once.
- 04
- Reconstruction
- Exact organiser images; published model; portable paths; offline cache.

**Speaker notes:** The primary submit.sbatch now selects the measured winning TP4-to-TP8/EP8 layout, concurrency 48 and the exact NIXL module hash. It allocates 16 GPUs, deploys three workers and the gateway, initializes two P/D pairs, then invokes the unchanged official AIPerf command in the same job. Image/model metadata, the patch as text, pinned tokenizer cache and package-relative replay instructions support reconstruction under a dedicated account.

## 16. Correctness claims follow the available evidence

- Published FP8 weights and BF16 KV, unchanged
- Worker logs / source
- Plain PD on 16 GPUs; no speculative decoding
- Configured / local logs
- Best long run / N48 latency gate
- 97.44% pass fraction
- Full-set accuracy ≥ 99% of reference
- Not yet tested
- Organiser reconstruction + official scored re-run
- Pending
- Local latency evidence is available. Official acceptance and any Bonus validation remain pending.

**Speaker notes:** The model checkpoint and precision remain unchanged; all requests use plain PD without speculative decoding or skipped computation. The descriptor patch is intended to preserve byte geometry, but local latency and CPU geometry checks do not establish the full-set accuracy gate. The organisers accuracy threshold is 99% of their own FP8 reference score. No accuracy pass, official score or verified Bonus claim is made.

## 17. Topology coverage complete; submission work remains

- Measured coverage
- 14 original + 3 EP2 layouts / All four concurrency sweeps / Winning long-run evidence / Both NIXL patches and logs
- Still outstanding
- Full-set accuracy check / Packaged job GPU replay / HPC/OpenFOAM evidence / Official upload and re-run

**Speaker notes:** Fourteen original layouts plus three explicit EP2 replacements are measured at all four concurrency points. Measuring a layout does not imply that it passes the SLA. The Qwen package contains the winning entry, source patch, English presentation and raw evidence. The full-set accuracy check, packaged orchestration GPU replay and official re-run remain separate validation steps. HPC results were not supplied for this Qwen-scoped workspace.

## 18. Current winner: TP4 prefill + TP8 / EP8 decode

- 1,912.30
- good output tokens per second
- 97.44% request SLA fraction  ·  N48 / 16 H200  ·  Official FP8 model
- Accuracy and organiser re-verification remain pending.

**Speaker notes:** The declared current winner is 1912.30 good output tokens/s with 97.44% SLA at N48 on 16 H200 GPUs. The organisers supply the checkpoint, images, cluster and locked benchmark. Our contribution is topology/load selection and request-scoped descriptor preparation. All usable search layouts are measured. Official acceptance still depends on organiser reconstruction and accuracy checks.

## 19. Appendix: the final repaired layout and selection

- Final layout
- P8-TP8-EP2_D8-TP8-EP8; job 22809 completed.
- N32 long run
- 1,507.96 good tokens/s; 95.38% SLA; no errors/cancels.
- N40 / N48 short sweeps
- 89.50% / 86.06% SLA: both miss the 90% gate.
- Selection
- Job 22415 remains the best passing long measurement.
- Interpretation
- Measured coverage does not mean every layout passes SLA.

**Speaker notes:** Job 22809 completed the final repaired P8-TP8-EP2_D8-TP8-EP8 layout with four short sweeps and a long N32 confirmation. N40 and N48 reached only 89.50% and 86.06% SLA, below the 90% gate. N32 passed with 1507.96 good tokens/s and 95.38% SLA, but did not beat job 22415. Unpatched job 22750 points remain distinct and are not combined into the patched sweep.
