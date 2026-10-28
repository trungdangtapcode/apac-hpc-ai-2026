# Current AI / Qwen handoff

Updated 2026-10-28T01:59:13.515328+00:00. This fork 01a166eb-33cb-7ce0-9699-ec65de26689a continues AI parent 01a15dd3-3094-7712-a991-8ce55b15cbfe and owns AI/Qwen only. Preserve the separate HPC worker. Chat Vietnamese; work artifacts English. No background Codex, schedules or automatic chat notification.

## Current jobs and dispatch handoff

| Cluster | Job | Purpose | Last verified state |
|---|---|---|---|
|H200 / Slurm|26847|CPU-only exact dynamic tokenizer-ID check|Proof PASS; query terminal state separately|
|H200 / Slurm|26849|Full N64 same-runtime tokenizer-off control|SUBMITTED / PENDING|
|H200 / Slurm|26851|Prefill dynamic tokenizer, max32, wait200microseconds|SUBMITTED afterany26849 + actual ID proof guard|
|H200 / Slurm|26853|Same, wait2milliseconds|SUBMITTED afterany26851 + actual ID proof guard|
|H100 / PBS|225306.pbs111|One same-node P4/D4 EAGLE unit|FAILED 127 before AIPerf; R2 prepared, not submitted|

These are dated snapshots; query actual queues before action. H200 serving jobs request 16 GPUs/two nodes/17 minutes maximum, own cap 5. The H100 job requests eight GPUs/one node/30 minutes, maximum 512 SU; combined CPU+AI PBS cap 3 and maximum one running AI allocation. The separate CPU queue was empty immediately after PBS admission; do not infer it remains empty. Preserve queue positions and frozen payloads.

[H200 load-bracket plans and actual receipts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-full-load-followups-20261026/REVIEW.md). [H100 full N24 admission, controls and limits](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h100-equal-tp-bench-admission-20261026/REVIEW.md). 26473 passed at 2661.889812 good tokens/s but lost; 26475 correctly failed the joint SLA at 57.151899% (677 TTFT breaches). All R3 chunk arms now pass locally; see the latest result table and continuation below. Job 225306 never ran AIPerf; preserve the launcher failure. [Actual chunk receipts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-prefill-chunk-full-20261026/ADMISSION.md).

## Latest reviewed performance

| Observation | Good output tokens/s | Joint latency pass | Interpretation |
|---|---:|---:|---|
|H200 R3 chunk8192, 26766|3045.501509|98.580442%|New full local pass; recovers historical level, not a matched runtime gain|
|H200 R3 chunk10240, 26768|3034.088251|98.523985%|Full local pass; lower than fresh8192|
|H200 R3 chunk12288, 26770|3020.943099|98.310454%|Full local pass; lower than fresh8192|
|Historical H200 25366/25373/25487 mean|3044.400475|Retained passing observations|Historical mean; approximately reproduced by new8192, no causal runtime attribution|
|H200 exact legacy replay 26313|2830.923547|98.427850%|Actual operational parity; 7.012117% below old mean|
|H200 full modern graph/cap 64, 26317|2829.604300|98.426966%|Valid local full observation; no useful new gain|
|H200 full modern graph/native, 26319|2827.996286|98.424311%|Control for current N62/N66 bracket|
|H100 fresh full N54, 225227|2399.186728|98.015873%|0.347131% below retained 222551; no unchanged repeat|

All latest full observations have zero profiling request errors/cancellations, smoke 7/8 without regression and retrieval 12/12. Every score is raw AIPerf Goodput requests/s multiplied by 200. Do not mix H100/H200 scores as matched configurations. H100 retained best individual 222048 remains 2433.019859 tokens/s. Official full-set 99%-reference accuracy remains UNKNOWN; small checks do not certify it. Packaged AI primary remains unchanged N62 pending reviewed authorised promotion.

The complete four-arm H200 graph/admission study passes all local gates: disabled/cap 64 = 2807.325653, breakable/cap 64 = 2829.604300, breakable/native = 2827.996286, disabled/native = 2802.498990 tokens/s. Graph gains +0.793590% / +0.909806% and native admission changes -0.171931% / -0.056828% are below the prospective >1% useful-gain gate. Close this tuning branch without selecting a favorable subthreshold peak for confirmation. One ordered deployment per cell cannot prove causality. [Full review, actual runtime comparison and sealed evidence](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-factorial-review-20261026/REVIEW.md).

## Distinct current hypotheses

Full N62/N66 now completed at 2823.776622 / 2826.104466 good tokens/s, both complete local gates PASS, zero errors/cancellations, smoke 7/8 and retrieval 12/12. Neither beats contemporary N64; close the immediate concurrency branch. [Full raw review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-full-load-review-20261026/REVIEW.md). Jobs 26473/26475 are now terminal and the smaller-chunk branch closes. [Raw smaller-chunk review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-small-chunk-review-20261027/REVIEW.md). The next declared 12288/HPC-Ops interaction retains the old 12288/auto-decode loss and is paired with a fresh 8192 control; no broad sweep or presumed gain.

H100 225228 F/0 in 6:39 passed eight distinct H100 device/source/metadata receipts, one independent eight-token semantic response and actual equal-TP send_kvcache/send_aux start/return markers on all four sender ranks without exceptions. Old 224560 lacked KV observer evidence because the checker watched a heterogeneous method; original failure remains. The new functional prerequisite is not a throughput or official accuracy pass. [Independent H100 review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h100-review-225227-225228-20261026/REVIEW.md).

225306 tests full N24 performance of one eight-GPU EAGLE unit. It preserves parent native serving/observer arithmetic and source pins; actual semantic/metadata gates precede scoring, then raw profile and local output gates. One unit is not a same-resource comparison against 16-GPU N54. A necessary per-unit feasibility threshold of 1235.581165 good tokens/s for a hypothetical 3% aggregate gain is not proof of linear scaling. Any future 16-GPU replica score must be actually measured. Do not scale or retry unchanged before reviewing the actual run.

26337 also passes small synthetic NIXL/UCX writes on 16 distinct H200s: 32 writes, 6,160,384 bytes total across three phases, all receiver buffers/sentinels validated. It repairs the earlier source-mount prerequisite failure. No model/SGLang bootstrap/real KV/TP collective/throughput is proven; do not relaunch the old failed full topology unchanged. [Component boundary](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-26337-20261026/REVIEW.md).

## Access, credit and admission

At 2026-10-27T17:56:03.194845+00:00, both authorised AI and CPU SSH helpers report no live VPN session. Both PBS queues are UNKNOWN; no new authentication prompt was sent. Earlier working AI access and CPU-only authentication failures below are historical. Preserve other worker channels and do not restart VPN. Fresh CPU queue availability is UNKNOWN, so PBS R2 admission has not occurred. No phone-side DUO approval or exact session lifetime is claimed. Preserve healthy private session state; never capture it or restart it gratuitously. Selected AI project 59010042 snapshot label 27/10/2026-00:20:07: grant 64000, used 48313.842, balance 15686.158, In Doubt negative zero SU. The owner explicitly removed internal withholding: all 4512 SU of terminal local holdbacks are released; historical maxima and charge-attribution limits remain audit metadata. Actual available balance is 15686.158 SU with zero discretionary/terminal buffer. Count genuinely active/uncertain commitments once, net of site prepayment. Owner's earlier 30 October planning deadline remains.

PBS admission checks both own queues and selected project credit under CPU-before-AI locks. A parser initially rejected signed negative zero before any reservation/qsub; it was fixed/tested, remote checksums reverified and exactly one definite new receipt obtained. No uncertain attempt remains. No budget increase or other worker spending occurred. Read nscc-budget.json and actual receipts before another admission.

## Inspection, history and backup

Inspect tails/errors/concurrency, role-local queues/KV, transport/runtime, CPU/GPU/VRAM and cost. H100 225227 scored-admission envelope has 24 samples per role, decode activity 99.990%, prefill 91.542% / 91.427%, 72 HTTP 200 polls. Earlier allocation-wide means include startup and measure a different interval. Activity is not FLOPS; VRAM is not token occupancy; node-wide low CPU does not exclude a hot serving thread. Historical helper host-memory TiB labels were wrong: division from KiB by 1024 squared produces GiB; raw bytes and scores unchanged. [Correct window and units](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h100-score-window-225227-20261026/REVIEW.md). Uncalibrated host skew and sparse request-start envelopes are not exact phase clocks. Missing telemetry is not zero.

[Readable illustrated learning checkpoint](../reports/ai-research-learning-journey-20261023/FULL_WORKLOAD_CHECKPOINT_20261026.md), [complete journal](../reports/research-journey-20261019/journal/README.md), [preceding handoff with older losses/corrections](history/20261026-ai-before-1450-condense.md). Earlier snapshots in history are not live.

Edit active sources once. Capture explicit safe small milestones, screen/verify, commit with actual dates and push the existing private origin. Frozen raw evidence and large-object hashes are preserved; GitHub push does not upload the sibling external artifact store. No slide/submission/HPC payload changed in this continuation. Continue justified research when queue/budget/evidence permit; this never enables background Codex or schedules.

## New owner steering and actual admissions — 2026-10-26T17:31:58.694229+00:00

Owner removed all AI internal SU buffers. Twelve terminal local holdbacks totaling 4512 SU are released; historical maxima/terminal receipts remain audit metadata, without claiming individual charge reconciliation. Fresh selected AI balance 15686.158 SU, internal buffer 0. [Policy proof](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h100-no-buffer-policy-20261026/POLICY-APPLIED.json).

H200 26436 N62 and 26438 N66 completed 0:0 with 2823.776622 and2826.104466 good tokens/s; both full local gates pass but no gain against N64. Earlier active snapshots are historical. Actual next Slurm jobs 26473 chunk 6144 and 26475 chunk 4096 are submitted, 16 H200/two nodes/17 minutes each, full N64; 26475 afterany 26473.

H100 225306 F/127 after 6:41: source/device/metadata/semantic gates pass, but external timeout cannot directly execute the PBS srun shell function. No benchmark ran. Root added that faulty boundary; derived R2 runs sourced shim inside timed Bash. Actual shim isolated-PATH regression reproduces 127 and corrected 0. R2 prepared, not yet submitted. Existing CPU read-only SSH command times out; one separate auth attempt did not establish a working channel. AI SSH works. Do not claim CPU queue is empty or restart VPN. No HPC payload/ledger changed.

Dispatch correction from owner: after payload checks pass, submit the justified ready followup promptly; do not prolong redundant review while the research queue is empty. This does not remove source/output gates, queue caps or permit blind duplicates. Actual new Slurm receipts are 26473/26475. PBS repair remains prepared pending a fresh CPU queue check. No background Codex or schedules.

## Actual storage incident and dispatch — 2026-10-27T02:31:10.224549+00:00

26521/26524 and derived 26531/26533 failed before model startup due to g4 default Enroot ENOSPC; no performance score. Probe 26526 confirms g4 /data about 2.65 GB free, g1 /data about 12.34 TB free, own default rootfs directories empty, local NVMe about 360/435GB free. Shared /home and /scratch also nearly full. No other user files or retained evidence were deleted.

The standalone Enroot variable fixture passed, but actual Pyxis filters ENROOT_DATA_PATH. Preserve the failed deployment and this correction; do not repeat that override. The next supported user-level route runs native Enroot under unchanged Slurm allocation/cgroup, with explicit source mounts and correct global-versus-relative GPU ID handling. Actual one-GPU prerequisite 26538 remains pending. Conditional full jobs 26545/26547 are queued; explicit actual CUDA proof required before a model starts. [Review and source references](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/native-enroot-serving-20261027/REVIEW.md). No throughput improvement or official accuracy is claimed.

H100 AI SSH still works, queue empty; fresh selected site label 27/10/2026-10:00:01 retains used 48313.842/balance 15686.158 SU, zero discretionary/terminal buffer. CPU SSH authentication is still unavailable, so the fresh combined PBS queue gate cannot be met. Prepared EAGLE R2 has NOT been submitted. No VPN restart or repeated credential guessing; no HPC queue/budget change.

## Actual four-job dispatch — 2026-10-27T03:41:21.453640+00:00

26538 completed 0:0 in 39 seconds: real Harbor image executes CUDA on one H200 using native node-local Enroot. Full 26545/26547 then failed in the second prefill NVIDIA hook, which rejects global device4 while the step-visible CUDA indices are0–3. The global-versus-relative distinction was logged but the CLI expectation was wrong. Preserve both failures; no AIPerf score exists.

Actual new jobs26574/26579/26581/26583 provide one split8 prerequisite and three full N64 arms (8192 control,10240 intermediate,12288 larger). The owner explicitly requested3–4 queued jobs; all four were admitted under cap5 and definite IDs retained. All original acceptance/quality/runtime gates remain, and actual eight-distinct-GPU CUDA proof is mandatory before model steps. No background Codex, blind duplicate, fixed-source edit or HPC action. [Review and receipts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/native-gpu-map-r2-20261027/REVIEW.md).

## Actual runtime R3 continuation — 2026-10-28T00:56:03.194845+07:00, Vietnam time

The four previous jobs are terminal: 26574 split-eight CUDA PASS; 26579 FAILED 1:0 after 8:54 because the native AIPerf image entrypoint interpreted env as a subcommand; 26581 FAILED 1:0 after 5:24 on router local-space guard; 26583 FAILED 1:0 after 6 seconds on initial prefill local-space guard. No profile score was produced. Native worker/source/KV and both semantic routes passed in 26579 before the client launch failed.

New 26764 completed 0:0 and verified the actual AIPerf exec-rc repair. Both node scans found no matching own native rootfs leftovers. Do not claim old rootfs leakage caused the transient capacity failures, or that the probe exercised removal. Actual frozen full arms 26766/26768/26770 are queued, preserving full protocol, source and output gates. [Repair, actual receipts and limits](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/native-runtime-r3-20261027/REVIEW.md). Historical results remain unchanged; no new performance gain or official accuracy is claimed. H100 access currently has no live VPN session, so R2 is not submitted. No HPC action or background Codex.

## Full chunk review and new tokenizer branch — 2026-10-28T08:59:13.515328+07:00, Vietnam time

26766/26768/26770 all completed0:0 and independently pass full raw protocol, actual runtime/KV/semantic and local output gates. Scores3045.501509/3034.088251/3020.943099 good output tokens/s; all have zero profiling errors/cancellations, smoke7/8 and retrieval12/12. Larger chunks lose and worsen p95 TTFT, so close the current chunk branch. The new8192 observation recovers the historical score level; it is not evidence that native Enroot caused a speedup. Official accuracy remains UNKNOWN. Actual batch-level cleanup removed four own rootfs trees in each full allocation after workers stopped; unlike the earlier zero-root probe, deletion is now exercised successfully.

New accepted jobs26847/26849/26851/26853 test prefill-only native dynamic tokenizer batching: CPU exact-ID proof plus fresh disabled control and max32 at200microseconds/2milliseconds. Both waits already returned exact equality for64 concurrent and one single input; full candidate jobs still require the proof and resolved runtime flags. This is a bounded frontend hypothesis, not proof of a CPU bottleneck or repeated N68 sweep. [Plan, native source and actual receipts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-dynamic-tokenizer-20261028/PLAN.md). H100 helper again reports no live VPN session; no qsub or MFA request. No HPC action, package promotion or background Codex.
