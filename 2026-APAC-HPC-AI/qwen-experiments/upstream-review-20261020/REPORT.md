# Upstream Qwen update review — 20 October 2026

## Finding

The fetched public repository is seven commits ahead of the retained checkout. Local HEAD is `5a67229942589c9559a8ba5e404bbd08ae91c6e2` (26 September); remote main is `3d050964d1008b97fb6d0d7ec5160087cd6883d9` (10 October, 11:02:08 +08:00). There is no later commit in the fetched main history at this check. This is new relative to that checkout, not evidence of a new change published today or a claim that every idea was previously unknown to our research.

The Qwen task-rules file has **no byte change** between those revisions. The README only renames its reference-script path; scoring tiers and percentages were already in the September addendum. The relevant additions are the Firmus worked scripts, PBS/Enroot application notes, ASPIRE scripts and actual H100 logs/exports. OpenFOAM additions were counted but not developed or copied into the Qwen evidence snapshot. HPC_Task remains untouched.

## What is useful

1. **Authoritative H100 reference evidence.** The new ASPIRE deployment uses two TP4 prefill replicas and two TP4/EP4 decode replicas, across all sixteen H100 GPUs. Published runs clear the fraction gate at N24 and N32 and fail it at N48/N64. The failure is driven by ITL, illustrating why a larger raw throughput is not automatically a qualifying improvement. Recomputed from each JSON's Goodput × 200:

| N | Good output tokens/s | Good-request fraction | Eligible |
|---:|---:|---:|---|
| 24 | 1053.821565 | 0.986343 | Yes |
| 32 | 1173.718122 | 0.908407 | Yes |
| 48 | 507.600050 | 0.308809 | No |
| 64 | 154.939710 | 0.081126 | No |

These are published starting points for this particular split, not the best achievable H100 result. Our retained H100 peak 2433.019859 uses two TP4/EP1 prefill replicas and one TP8/EP8 decode replica with additional serving changes. The two sets are contextual measurements, not a new matched experiment or an attributable speedup. Do not mix their raw numbers with H200 rankings or call the difference a controlled optimisation gain. [Exact parsed fields and hashes](official-h100-reference.json).

2. **PBS container support is documented directly.** ASPIRE supports native PBS Enroot creation on each allocated node. The notes cover container resource keys, cross-node environment and mount handling, allocation identity when launching remotely, AIPerf entrypoint quoting and the need to inspect actual exports rather than only shell exit status. Our current accepted PBS stack uses a tested Singularity wrapper instead. Both methods are permitted; swapping wrappers is an environment change that needs a bounded smoke test and source/library validation, not an automatic scoring improvement.

3. **A concrete way to save startup time and credit.** The notes demonstrate parallel host reads of model shards before worker startup and report much shorter load times for their run. Their TMPDIR warning also explains why a missing in-container socket directory can disable custom all-reduce. Our current wrapper already provides private writable /tmp and enforces source/runtime checks; its launch path does not include that explicit once-per-node shard-read step. The worker's existing `--weight-loader-prefetch-checkpoints` is not the same operation. Host page-cache prefetch is a plausible future cost experiment, not evidence of faster scored inference or a promised repeatable loading reduction on our nodes.

4. **Shared reproducibility assets.** Public SGLang 0.5.17 CUDA 12.9 / AIPerf 0.12.0 images and the official FP8 model revision are identified in the notes. These can reduce private-account setup dependencies when rebuilding. Our current image is a separately pinned artifact; matching a package version does not prove identical native libraries or kernels. Do not change image paths or source guards without comparing provenance and testing the new execution path.

5. **The provided splits are reference examples.** Firmus scripts 07, 08 and 09 exercise different prefill/decode widths and ratios, not a requirement to copy one. Our research has already explored those families and goes beyond their two-TP4-decode reference. The added files justify checking our deployment and documentation, not paying for blind repeats of already measured layouts.

## What does not change

The official closed-loop command, 4000/200 synthetic targets, workload seed 2026, cold-prefix cache busting, TTFT 3000 ms / ITL 20 ms and minimum 0.90 fraction all predate this update. Goodput × 200 is explicitly written in the retained Qwen addendum. The ASPIRE worked-results paragraph uses raw throughput times fraction; its four published exports numerically agree with Goodput × 200, but the official rule and previously supplied clarification remain the scoring authority.

The current benchmark script uses the official Hugging Face tokenizer ID with a pre-staged offline cache; it does not substitute the local model path for that measurement tokenizer. Existing experimental durations and warmup are not changed in frozen bundles. The recommendation to use shorter exploratory runs was also already present in the September rules, not a new relaxation. Keep short screens labelled exploratory and require a full-protocol final confirmation.

## Decisions and next steps

- Retain the active measured worker/topology branch and frozen queue payloads. No GPU job is submitted solely because reference scripts were added.
- For a later derived cost experiment, measure startup phase boundaries and model-load times, then compare once-per-node shard prefetch against the same launch without it. Keep the official scoring interval unchanged, count the prefetch in allocated walltime/SU, and avoid an unbounded read sweep. Hardware and filesystem cache state must be reported; no causal claim comes from the documentation's numbers alone.
- Treat native Enroot and public assets as a separate reproducibility route. First validate image digests, the exact SGLang/NIXL/native interfaces and mounts; then use a small bounded scheduled smoke if needed. Do not replace an accepted wrapper during a scoring trial.
- Preserve the current model-quality limitation: local checks are not the organiser full-set 99%-reference accuracy verification. No submission package, slide, scheduler policy, budget or authentication material is changed by this review.

## Provenance and recovery

This review used `git fetch --no-tags origin main`, not pull/merge/reset. Active source HEAD and tracked working files remain unchanged. `comparison.json`, `commits.txt` and `qwen-changes.diff` identify the exact revision delta. `snapshot/` retains the Qwen public documents, scripts and raw reference logs at that SHA; `source-sha256.json` seals their downloaded bytes. `official-upstream.bundle` preserves the fetched public Git history and passes bundle verification. It also contains the public upstream HPC history as Git objects, although the inspected file snapshot is Qwen-scoped. These are reference artifacts, not our failed or successful GPU jobs. Scheduler and credit state were not refreshed for this repository-only question.

Sources pinned to this review:

- [Latest commit](https://github.com/hpcac/2026-APAC-HPC-AI/commit/3d050964d1008b97fb6d0d7ec5160087cd6883d9).
- [ASPIRE notes](https://github.com/hpcac/2026-APAC-HPC-AI/blob/3d050964d1008b97fb6d0d7ec5160087cd6883d9/3.2%20Qwen3%20Application%20Notes%20-%20ASPIRE%202A%2B.md).
- [ASPIRE scripts](https://github.com/hpcac/2026-APAC-HPC-AI/blob/3d050964d1008b97fb6d0d7ec5160087cd6883d9/3.2-aspire2p-scripts/README.md).
- [Firmus reference script guide](https://github.com/hpcac/2026-APAC-HPC-AI/blob/3d050964d1008b97fb6d0d7ec5160087cd6883d9/3.1-firmus-scripts/README.md).
- [Qwen rules, unchanged across this delta](https://github.com/hpcac/2026-APAC-HPC-AI/blob/3d050964d1008b97fb6d0d7ec5160087cd6883d9/1.%20Qwen3%20AI%20Task%20Rules.md).
