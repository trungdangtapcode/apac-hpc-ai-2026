# DeepInfer review: two useful leads, no engine migration

Reviewed 20 October 2026. **Keep the current official FP8 Qwen/SGLang PD stack. Investigate actual worker CPU locality and a lossless EAGLE3 draft before buying another broad engine experiment.** This is a source-backed research decision, not a new performance result.

## What the pasted assessment gets right

The [DeepSeek repository at pinned commit 774ce244](https://github.com/deepseek-ai/DeepInfer/blob/774ce244b87cc0eb8d4b94ab9f5de2ab22049f01/README.md) lists DeepSeek-V4.1-Flash and SM100/Ascend 950, and releases offline inference. It does not list Qwen or Hopper. Its published chart uses four SM100 GPUs for prefill and 64 for decode; that is not a matched 16-H200 result. The open release also leaves service-level KV management, PD integration and replica load balancing to the deployer. No evidence here establishes a fastest engine for our task.

The [deployment Q&A](https://github.com/deepseek-ai/DeepInfer/blob/774ce244b87cc0eb8d4b94ab9f5de2ab22049f01/doc/inference_deployment_qa.md) discusses much wider expert parallelism than our 16-GPU limit. Its production scale and performance claims are publisher claims, not independently reproduced contest results. Whole-engine support must be distinguished from individual kernel libraries: our existing DeepGEMM kernels already execute on Hopper.

The pinned README, deployment Q&A, license and dependency files are retained under source/. Nothing from DeepInfer was built, installed or executed. Git commit time is retained in commit.txt; this review does not infer release age from search-cache freshness.

## What must be corrected for this contest

The generic BF16 TP8 × two replicas command is unsuitable for our Basic submission. The [actual task rules, including Q1](https://github.com/hpcac/2026-APAC-HPC-AI/blob/3d050964d1008b97fb6d0d7ec5160087cd6883d9/1.%20Qwen3%20AI%20Task%20Rules.md) require the published Qwen3-235B-A22B-Instruct-2507-FP8 target, plain separated prefill/decode, all 16 GPUs and traffic through the gateway. Two or four ordinary colocated replicas do not satisfy that Basic deployment. BF16 KV remains allowed; BF16 target weights do not. A compatible vLLM PD implementation is not forbidden, but introducing another serving stack requires transport, correctness and deployment work; the pasted colocated command does not provide it.

FP8 does not universally force TP4. [Qwen's vLLM guidance](https://qwen.readthedocs.io/en/latest/deployment/vllm.html) explains backend-dependent block divisibility and TP/EP alternatives. Our actual TP8/EP8 FP8 decode worker is stronger local evidence than a generic memory-capacity estimate. Fitting weights in VRAM is not evidence of goodput or compliance.

Keep the official closed-loop workload: 4000 input / 200 output tokens, seed 2026 and cold prefixes. Rank by AIPerf Goodput in requests/s × 200, with joint TTFT ≤ 3000 ms and request-mean ITL ≤ 20 ms, fraction ≥ 0.90 including errors. Do not substitute total throughput, acceptance length or TPOT aggregates for this score. Official full-set accuracy at 99% of reference is still unverified.

## Which ideas are new for our retained stack?

| Idea | What is already known here | Decision |
|---|---|---|
| DeepGEMM | Already used for dense projections and selected prefill; H200 25020 passed 256 micro cases without a consistent alternative-provider win. | Keep; not a new switch. |
| Asynchronous CPU scheduling | Actual worker logs have disable_overlap_schedule=False. | Already enabled; inspect remaining host overhead rather than claiming a new gain. |
| Attention DP + MoE EP / DeepEP | H200 historical DP8/DeepEP jobs 23780/23859 reported 2549.20/2538.08 good tokens/s at N52; contemporary MNNVL 23778/23839 gave 2592.16/2592.92. N54 followup 23934 gave 2555.42. | This broad architecture was tested. Do not repeat unchanged settings merely because DeepInfer recommends it. Current EP8 is not proof that DeepEP is enabled. |
| Expert load balancing | Current enable_eplb=False; current aggregates do not identify per-expert/rank skew. | Only reopen with measured imbalance and a backend-compatible exact expert remapping. Adding replicas/migration consumes memory and time; dropping experts is forbidden. |
| CPU/NUMA locality | New sealed one-GPU H100 probe finds allowed CPU NUMA 0 versus GPU NUMA 1. | Collect full-serving worker mapping before an affinity intervention. |
| Lossless speculative decoding | Current speculative_algorithm=None. A public EAGLE3 draft exists for the exact original Qwen checkpoint. | New concrete candidate; source/metadata screening done, runtime compatibility unresolved. |
| FlashMLA / SWA replay / DSpark | DeepSeek architecture-specific paths; Qwen's attention is not a drop-in replacement. | Do not transplant the bounded 140-token replay setting, truncate prompts, skip attention or use unverified draft acceptance. |

Historical DeepEP numbers come from [SERVING_TUNING_RESULTS.md](../SERVING_TUNING_RESULTS.md). They are earlier stack observations, not fresh matched comparisons with today's 3022.034919 H200 result. Named collective durations in 24915 account for 23.529% of summed recorded kernel time, not 23.529% of wall-clock critical path or a promised recoverable speedup. They justify inspection, not an automatic DeepEP win.

## Lead 1: verify CPU locality in the actual serving allocation

[Probe 222412](../cpu-gpu-locality-20261020/REVIEW.md) verifies payload hashes and static capture. Its 28 allowed logical CPUs are all on NUMA 0; its allocated H100 PCI locality is NUMA 1, with no intersecting CPUs. It costs 2.773333 SU and is already reconciled. This observation predates this review's new hypotheses and was not a new DeepInfer experiment.

A NUMA node groups CPUs with nearby memory and devices. Remote placement can add host-side delay, but this one-GPU allocation does not establish the masks, memory placement or CPU demand of sixteen-GPU serving. Before changing anything, a later derived baseline should collect each worker's allowed CPU mask, rank, GPU UUID/PCI and local-list intersection on both nodes, with bounded thread-load sampling if available. Keep monitoring identical in any subsequent control/candidate comparison; measure its overhead outside ranked scoring first.

If the real serving mapping exposes remote placement and enough scheduler-allowed local CPUs, compare the original binding with a deterministic local mapping, keeping image/model, workers, TP/EP, kernels, chunk size, load, benchmark and observers fixed. Use an existing planned derived run to collect mapping where possible. Never change frozen queued payloads or silently assume cpuset/NUMA numbering is shared between H100 and H200. Reject a change with new output failures, missing runtime evidence or a worse joint SLA. A static capture is not a performance measurement.

## Lead 2: lossless EAGLE3, using a real draft rather than porting DSpark

The [Nebius publisher card](https://huggingface.co/nebius/EAGLE3-Qwen3-235B-A22B-Instruct-2507/blob/ff0f0c0999f6c86b21dfd2f5803eebc4ac712224/README.md) identifies a draft trained for Qwen3-235B-A22B-Instruct-2507 using general Infinity-Instruct responses, with CC BY 4.0 licensing. We retained that revision's card/config and public metadata only, not weights. The card demonstrates an original-target vLLM example, not our FP8 SGLang/PD configuration. Its acceptance-length results on other tasks are not throughput predictions for Shakespeare/N62. Public training metadata is a declaration, not an independent audit proving the absence of every contest example.

The idea is to let a small helper propose several tokens, then have the unchanged official FP8 target verify every accepted token. Under official greedy settings the emitted token sequence must match target-only decoding. A high acceptance rate alone does not establish this. The [official Q1 rule](https://github.com/hpcac/2026-APAC-HPC-AI/blob/3d050964d1008b97fb6d0d7ec5160087cd6883d9/1.%20Qwen3%20AI%20Task%20Rules.md) allows lossless drafts, including higher-precision draft weights. Do not inherit target FP8 quantization onto an unquantized draft accidentally. Do not serve the draft as the target, including through auto-generated hosting snippets on Hugging Face.

[Current SGLang speculative documentation](https://docs.sglang.ai/advanced_features/speculative_decoding.html) describes EAGLE3, but current public docs do not certify our pinned image. CPU-only extraction of five native files succeeded; their syntax parses, and the native NIXL SHA matches the original SHA recorded by our frozen transport patch. [Preflight record](preflight.json) and [extraction hashes](runtime-extraction-corrected.json) retain the scope. The initial -cat extraction failed because this installed unsquashfs lacks that option; a corrected bounded extraction to a fresh directory succeeded. No runtime modules or remote model code were executed.

The pinned source has EAGLE3 argument hooks, draft-KV registration, and hidden-state metadata paths. Native NIXL anticipates extra destination KV regions for decode-only speculation. That is encouraging interface evidence, not a completed integration gate: we have not validated the draft's architecture/weight-key conversion, Qwen3MoE FP8 hidden-state layer mapping, prefill draft-state setup, heterogeneous TP4→TP8 patched geometry, verification kernels/graphs or numerical equivalence. Draft recurrent state and KV geometry cannot be assumed identical to target KV. Mere argument acceptance would not prove them correct.

Next finish those CPU source/loader/geometry checks. Only if they pass, prepare one derived H200 correctness pilot with the same official target, all 16 GPUs, plain PD and gateway, beginning with a small fixed speculation tree (two draft steps, top-k one, three draft-token slots if the pinned implementation validates that convention). Explicitly pin draft revision/precision and preserve target-only reference output tokens. Use generic prompts plus long-context diagnostics, then greedy token equality and full response/transport checks. A short unranked load probe must report accepted tokens per verification, draft/verify time, extra memory, errors and TTFT/ITL before any full scoring job. Never disable verification to inflate acceptance.

At N54/N62 the target is already processing many requests together. Extra drafting, larger verification batches and reduced KV capacity can outweigh saved decode steps. If compatibility fails, exact-token checks fail, or the bounded screen shows no plausible goodput improvement, close that implementation instead of launching a blind grid. Only a promising valid screen merits a fresh matched control/candidate under the full protocol and an independent confirmation. This does not replace official accuracy evaluation.

## Queue, budget and preservation decision

Read-only scheduler check at 2026-10-20T14:45:58Z: H200 24928/24962/24964/24965 are Priority-pending. PBS 222419 is Q, 222420 is dependency-held H. Preserve their positions. The last published ledger check at 14:21:57Z has 22761.603 SU balance; 2048 SU pending commitments and a 13000 SU buffer leave 7713.603 SU internal headroom. This is a dated balance, not a fresh spending authorization. Any later PBS pilot requires a new credit/queue check and reservation under the existing lock/caps.

**No new GPU job, engine installation, draft/model weight download, submission-package edit or background AI was performed for this review.** Existing queues are occupied. The immediate new work is compatibility/locality evidence, not buying an unsupported engine migration. Keep platform series separate and the 3022.034919 H200 / 2433.019859 H100 accepted individual peaks unchanged.

The source tree, hashes, failed extraction and reasoning are explicitly captured to the private archive as a separate research checkpoint. Git does not upload the sibling external artifact store. Earlier tutorial statements that no draft had been selected describe their historical snapshot; a concrete candidate is now identified, not yet validated or selected for deployment.
