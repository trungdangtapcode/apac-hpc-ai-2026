# Current AI / Qwen handoff

Updated 2026-10-28T16:31:19.728323+07:00, Vietnam time (UTC+7). This fork `01a166eb-33cb-7ce0-9699-ec65de26689a` continues the AI parent `01a15dd3-3094-7712-a991-8ce55b15cbfe`. Own AI/Qwen only; preserve the independent HPC worker, payloads, queues and budgets. Chat Vietnamese; all work artifacts English. No background Codex, schedules or automatic chat notification.

## Actual queue and next actions

| Cluster | Job | Purpose | Last verified state |
|---|---|---|---|
|H200 / Slurm|26949|Full N64 tokenizer-off control, warmup lifecycle repair|PENDING Priority|
|H200 / Slurm|26951|Same full runtime, prefill tokenizer wait 200 microseconds|PENDING afterany 26949|
|H200 / Slurm|26953|Same, wait 2 milliseconds|PENDING afterany 26951|
|H200 / Slurm|26988|Two-node CPU-only storage prerequisite for the published portable entry|PENDING Priority|
|H200 / Slurm|26990|One-H200 native BF16 page-size 1/16 correctness primitive|PENDING Priority|
|H100 / PBS|225306.pbs111|Earlier one-node equal-TP EAGLE benchmark attempt|FAILED 127 before AIPerf; R2 prepared, not submitted|

Five own Slurm slots are occupied. Do not add jobs beyond cap 5, cancel positions, mutate frozen payloads or call a pending job a measurement. Full serving jobs use 16 H200/two nodes/17 minutes. The page primitive uses one H200/eight CPUs/six minutes, maximum 0.1 GPU-hour. The storage preflight uses two nodes/zero GPUs/two CPUs per node/two minutes. These are dated states; query the scheduler before action.

Review the three full tokenizer arms when terminal. They retain fixed N64/4000:200/seed 2026/cold prefixes/full 60:120:30 and all raw source/runtime/KV/two-route/output gates. Their predecessors 26849/26851/26853 passed semantic response receipts but timed out before AIPerf; no score exists. The repair retains a 120-second semantic command and the existing absolute warmup/job envelopes, adding lifecycle markers. [Exact repair and failure review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-tokenizer-warmup-repair-20261028/REVIEW.md).

26947 completed 0:0 in 36 seconds on g4. Actual markers show root creation 19 seconds, native start to short-command return 9 seconds, removal 5 seconds. This CPU-only nonmodel case does not establish why old g1 semantic steps exceeded their combined timer. It is not a performance improvement. [Independent diagnostic review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/submission-replay-20261028/lifecycle-review-26947.json).

26988 checks compute-node Enroot capacity before spending a full allocation on portable-entry reproduction. The exact published N64 script tree is frozen, including its path with spaces. The real 16-GPU portable replay remains NOT_SUBMITTED; admit only after an actual usable preflight and a free slot, with fresh in-allocation checks because nodes and space may change. [Plan and definite receipt](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/submission-replay-20261028/PLAN.md).

26990 tests actual native BF16 NHD pool writes and FlashInfer paged decode attention over page boundaries and a partial final page, comparing page 1/16 with an FP32 oracle. It constructs only one layer and metadata-derived local head geometry. It does not observe full-model decode heads/layers, run prefill, register NIXL or measure model speed. Runtime source/device/shape/dtype and numerical checks fail closed. Page sizes above 1 also change automatic Qwen prefill selection from FA3 to FlashInfer, so a future full comparison cannot isolate a pure page effect without a backend-held control. Full P/D and prefill compatibility gates remain before any full model trial; never widen the current page-1 missing-head exceptions by assumption. [Source review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-kv-page-feasibility-20261028/REPORT.md), [primitive and receipt](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-kv-page-primitive-20261028/PLAN.md).

## Latest valid performance and decisions

| Observation | Good output tokens/s | Joint request SLA | Interpretation |
|---|---:|---:|---|
|H200 historical N64, 25366/25373/25487|3044.400475 mean|Retained full local passes|Three-run reference; no global optimum claimed|
|H200 native-runtime N64, 26766|3045.501509|98.580442%|Separate full local pass; recovers historical level|
|H200 chunk 10240, 26768|3034.088251|98.523985%|Lower than same-runtime chunk 8192|
|H200 chunk 12288, 26770|3020.943099|98.310454%|Lower throughput and higher p95 TTFT|
|H200 exact legacy replay, 26313|2830.923547|98.427850%|Valid lower observation retained; variation unexplained|
|H100 fresh N54, 225227|2399.186728|98.015873%|Separate platform and settings|
|H100 retained individual, 222048|2433.019859|Retained full local pass|Historical individual peak, not a matched H200 comparison|

Good output tokens/s = raw AIPerf Goodput requests/s × 200. Joint SLA is TTFT at most 3000 ms and request-mean ITL at most 20 ms, with at least 90% of all requests including errors. Current full runs have zero profiling errors/cancellations, smoke 7/8 without regression and retrieval 12/12. These small checks do not certify official full-set accuracy at least 99% of reference; it remains UNKNOWN. Actual generated token IDs are not retained in ordinary performance runs.

Close the larger-chunk branch: all three new arms pass but larger chunks lose. Full N68 historical gain is only 0.083056%; unchanged N62/N66 and graph/admission tuning did not clear the predeclared useful-gain gate above 1%. Decode-only EAGLE3 passed an unranked short screen but lost 4.74% versus its target-only control; unchanged speculation is closed. Do not attribute recovered approximately 3k performance causally to native Enroot versus older lower runs. H100 and H200 results remain separate. [Full chunk analysis](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-native-chunk-review-20261028/REVIEW.md).

## Access, budget and execution policy

The existing H100 SSH helper again reports no live VPN session in this turn. Phone-side DUO availability was asked earlier and has not been answered. No MFA request was triggered, and current CPU/AI PBS queues and credit are UNKNOWN. No fresh qsub occurred. Do not restart healthy sessions or copy authentication state. Failed authentication does not authorise repeated DUO prompts.

Last selected-project snapshot, dated 27 October: project 59010042 grant 64000 SU, used 48313.842, balance 15686.158, In Doubt negative zero. This is historical, not current spendable credit. Owner removed all internal discretionary/terminal holdbacks; buffer is zero. Count genuine pending/running/uncertain commitments once, net of actual site prepayment. Owner's 30 October planning deadline remains. Before any qsub, refresh BOTH own CPU and AI queues under CPU-before-AI locks, check project credit/ledger, combined cap 3 and maximum one running AI job. Prepared equal-TP H100 R2 is eight GPUs/one node/30 minutes/max 512 SU; it has not been submitted. Do not change the HPC worker's ledger or queue.

Continue justified research when a slot and valid gate permit. A status request is a checkpoint for that loop, not a reason to leave feasible work idle. A terminal error is not a valid measurement; an inaccessible queue is unknown rather than empty. Review resources beyond the score, label missing telemetry, and preserve losing/failing branches. No background Codex, watcher that starts AI work, schedule or automatic chat wake-up is enabled.

## Submission, inspection and preservation

The owner authorised the 28 October AI-only publication. The current team ZIP/PPTX use the replicated N64 AI primary and 32 updated AI slides. All 265 HPC files/modes and all 68 dependency parts for its eight slides remain unchanged. Package tests pass 591 checks; the portable entry has not been separately GPU-replayed. The latest ZIP is about 75 MiB after omitting six duplicate generated input captures with hashes; research originals remain preserved. [Delivery, PDF, notes and validation](ai-submission-update-20261028.md). Research queued jobs do not silently promote the package.

Inspect tail latency/errors, role-local queues/inflight/KV, transport/runtime, sampled CPU/GPU/VRAM and costs. Activity is not FLOPS, VRAM allocation is not KV token occupancy, sparse request-start envelopes are not exact phase clocks and low host-wide CPU does not exclude a hot thread. Preserve the recorded profiler HTTP500 correction and host-memory GiB/TiB label correction. The full scope and older branches remain in the [previous handoff](history/20261028-ai-before-page-primitive-093119.md) and [complete journal](../reports/research-journey-20261019/journal/README.md).

Edit active sources once, capture explicit safe paths into the existing Git archive, verify, commit small milestones with actual dates, push, and check origin/main equals HEAD. Never develop independent archive copies or capture weights/authentication/runtime caches. Large object bytes remain in the sibling artifact store; a Git push uploads their manifests, not those bytes. No automatic synchronisation or background Codex is enabled.
