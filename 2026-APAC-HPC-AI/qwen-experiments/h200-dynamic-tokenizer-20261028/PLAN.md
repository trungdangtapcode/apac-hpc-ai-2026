# Native prefill tokenizer batching

Recorded 2026-10-28T08:59:13.515328+07:00, Vietnam time. Accepted probe 26847 and full jobs 26849/26851/26853. Actual receipts are in probe-submission.json and submission-receipts.json. Only this AI track is changed.

The previous R3 full chunk study passed locally: 26766 chunk8192 = 3045.501509, 26768 chunk10240 = 3034.088251, 26770 chunk12288 = 3020.943099 good output tokens/s. All had zero profiling errors/cancellations, smoke 7/8 without regression and retrieval12/12. The larger chunks were lower and worsened p95 TTFT; close this bounded chunk branch. The incumbent has recovered the historical approximately 3044.4 level, but this is not a matched gain attributable to native Enroot or any cleanup change. A previous historical N68 increase was only 0.083056%, below the useful-gain gate; do not revive unchanged concurrency trials.

The current scored-admission envelope has 24 samples per role per run. For 26766, decode has 100% sampled GPU activity, mean50.333/max54 running requests and no sampled queue; prefill activity is96.417/97.156%, with mean queues1.292/1.208. Host-wide CPU busy is12.56/14.38%, which cannot exclude one hot frontend thread. These figures do not establish a CPU or GPU kernel bottleneck. The distinct hypothesis is that batching concurrent string tokenization can reduce frontend work/event-loop blocking and TTFT while preserving exact token IDs. Rust gateway preprocessing may bypass this worker route, and cold arrivals may not form batches; a negligible result closes the hypothesis rather than justifying broader sweeps.

Pinned actual-image TokenizerManager initializes AsyncDynamicbatchTokenizer when enabled and routes SINGLE_STRING input through encode. The native class uses the same tokenizer and kwargs through one ThreadPoolExecutor; a lone input is processed immediately, while an already queued burst is collected up to the maximum size/wait. Local source references are recorded in source-references.json; the primitive class was extracted from the actual image and hashed. The first extraction attempt rejected a precreated destination; retry to the empty absent directory succeeded before any probe submission. No GPU time was spent on extraction.

| Accepted job | Change | Bounds |
|---|---|---|
|26847|CPU-only exact tokenizer-ID functional prerequisite; 64 concurrent plus one single input at each wait|1 node, 0 GPUs, 8 CPUs, maximum5min|
|26849|Fresh R3 N64 control; dynamic batching disabled|16 H200, 2 nodes, maximum17min|
|26851|Prefill-only native dynamic batching; max32, wait0.0002seconds|Same full bounds|
|26853|Prefill-only native dynamic batching; max32, wait0.002seconds|Same full bounds|

The probe has returned EXACT_DYNAMIC_TOKENIZER_IDS_PASS for both waits, matching the exact single tokenizer IDs. Terminal scheduler and cleanup completion remain separately queried. The control retains only existing runtime prerequisites and does not depend on optional tokenizer proof. Candidate batches require the new proof before model startup, and actual resolved ServerArgs must show the requested flags/values on both P roles and unchanged disabled state on D. A runtime enabled flag does not count actual encode invocations; no direct tokenizer activation counter is collected in these frozen bundles.

All native model/precision/transport/GPU geometry, full60/120/30 N64 workload, fixed4000/200, seed2026 and cold prefixes remain. The two candidates differ only in maximum tokenizer batching wait. The official joint latency gate includes errors in its denominator; zero errors/cancellations and local smoke/retrieval gates remain. Unchanged benchmark/expected inputs/source patch/KV gate/launch/cleanup bytes were compared with the parent. Python AST, shell syntax, manifests and scheduler test-only checks pass. Submitted payloads remain frozen.

Judge candidate against the fresh control, including raw tails, request errors, server queues/KV and available hardware telemetry. Require a useful valid gain greater than1% without material tail regression before independent confirmation. A single full pass, exact tokenizer-ID equality, or high activity is not official full-set model accuracy. Official99%-reference accuracy stays UNKNOWN. No promise of improvement or global optimum is made.

Own Slurm cap5 is respected; four actual receipts were obtained. H100 helper returned no live VPN session, current PBS queues and credit are unknown; prepared H100 R2 remains unsubmitted. No MFA prompt was triggered. No HPC payload, CPU/GPU PBS ledger, submission package, slide or background schedule changed. Raw old failures and the historical higher individual N68 observation remain retained.
