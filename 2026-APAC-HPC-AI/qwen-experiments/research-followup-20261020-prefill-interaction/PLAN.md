# H200 prefill kernel interaction at fixed N60 and chunk8192

## Evidence and hypothesis

The current H200 incumbent uses DeepGEMM prefill/chunk8192 plus HPC-Ops decode. N60 unobserved runs reproduce around 2989–2992 good output tokens/s; the new observed control 24927 passes at 2971.312. Its scored samples show prefill GPU activity around 96.5%, mean per-GPU power 659–675 W, and roughly 133334 MiB sampled VRAM; decode activity is 100%. These are coarse resource samples, not proof of a bottleneck or power throttling. The separate diagnostic retains substantial named DeepGEMM and pre/post-processing kernel duration. GPU phase work is a reasonable next comparison without claiming a predicted speedup.

Earlier H200 HPC-Ops prefill/chunk4096 with auto decode independently measured 2732.459 and 2728.962 at N56, a small positive effect over matched controls. Both-phase HPC-Ops/chunk4096 at N56 passed at 2742.207; chunk6144 with auto decode was 2714.903. These do not establish the missing **HPC-Ops prefill + chunk8192 + HPC-Ops decode at N60** interaction. The later DeepGEMM8192/HPC decode gain proves that runner and prefill batch settings interact. H100 both-phase success motivates a direct H200 measurement, never conversion of H100 scores.

Hypothesis: HPC-Ops' fused gather/GEMM/activation/reduction path handles the larger prefill batch efficiently enough to improve the fixed-N60 deployment. Counterhypothesis: its SM90 kernels are tuned primarily for H20, so H200 DeepGEMM remains better or larger prefill chunks exacerbate latency. Native source explicitly warns that H100/H200 benefit is not guaranteed. The new pair changes one intended prefill runner, not a closed FlashInfer-prefill or chunk12288 branch.

## Exact matched pair

| Bundle | Prefill MoE | Chunk | Decode MoE | Load | Observer |
|---|---|---:|---|---:|---|
|s21-dg8192-hpc-n60-control|DeepGEMM|8192|HPC-Ops|60|On|
|s21-hpc8192-both-n60|HPC-Ops|8192|HPC-Ops|60|On|

Both derive from fully reviewed 24927 submitted bytes. Candidate worker inverse-diffs to the control after removing only its prefill backend selection and early Hopper/HPC symbol check; the inference command changes just prefill MoE backend. Benchmark, profiler, resource sampler, phase markers, topology, NIXL patch, native FP8 checkpoint, BF16 KV, FA3 prefill/FlashInfer decode attention, graphs1–64, MNNVL AUTO+PDL and all output checks remain byte-identical. No speculative decoding or skipped model/KV work. The pinned wrapper and previous H200 prefill runs establish support; actual runtime/ranks still require validation.

## Acceptance, interpretation and stopping

Review terminal seals, submitted hashes, raw complete 60/120/30 and 4000/200 protocol, per-request SLA/errors, all short/12-long checks and intended runtime delta. For prefill, allow only DeepGEMM→HPC-Ops and the inherited speculative-runner field while speculative decoding remains None; random seeds may differ. Validate BF16 KV and prefill Hopper/HPC preflight. Decode must remain unchanged on all ranks.

Inspect latency tails, admission/batch/KV logs and scored hardware/server samples, confirm disjoint UUIDs/coverage and deduplicate node counters. Profiles are separate N48 diagnostics and cannot establish causal end-to-end fractions. Compare candidate only with this equally observed same-load control; do not subtract the single 0.682% prior observer difference. Do not pool platforms or call this official accuracy.

A candidate gain of at least 1% with complete local gates warrants a controlled independent confirmation before adoption; smaller effects are inconclusive under observed deployment/observer variation. A clear loss or runtime/output failure closes this setting with preserved evidence, no blind chunk or load growth. The N62 repeat remains a separate question.

## Resource and provenance

Two 16-H200 Slurm allocations, at most 17 minutes each. Query real queue under the shared lock and remain within five active jobs; keep 24928/24962 positions. No PBS SU reservation or submission while VPN access/credit is unavailable. Do not change submitted payloads, clocks/power limits, official package or autopilot.

Primary deployed source: `../research-followup-20261020-0530/runtime-source/extracted/sgl-workspace/sglang/python/sglang/srt/layers/moe/moe_runner/hpc_ops.py`, selectively extracted read-only from the pinned local image. It documents fused blockwise FP8, global top-k/EP semantics, Hopper-only support and H20 tuning caveat. [Upstream HPC-Ops](https://github.com/Tencent/hpc-ops) is background; the actual pinned wrapper and raw deployed logs decide compatibility. Previous job summaries and full reviews are retained under runs/24529,24574,24640,24641 and the 18 October followups. Full new observer evidence is in ../research-followup-20261020-0530/RESULTS.md.
