# Current AI / Qwen handoff

Updated 2026-10-26T14:50:26.434276+00:00. This fork 01a166eb-33cb-7ce0-9699-ec65de26689a continues AI parent 01a15dd3-3094-7712-a991-8ce55b15cbfe and owns AI/Qwen only. Preserve the separate HPC worker. Chat Vietnamese; work artifacts English. No background Codex, schedules or automatic chat notification.

## Actual active research

| Cluster | Job | Purpose | Last verified state |
|---|---|---|---|
|H200 / Slurm|26436|Full native runtime, N62|PENDING: resources / unavailable higher-priority nodes|
|H200 / Slurm|26438|Same runtime, N66|PENDING afterany 26436|
|H100 / PBS|225306.pbs111|One same-node P4/D4 EAGLE unit, full N24 feasibility|RUNNING on a2ap-dgx013|

These are dated snapshots; query actual queues before action. H200 serving jobs request 16 GPUs/two nodes/17 minutes maximum, own cap 5. The H100 job requests eight GPUs/one node/30 minutes, maximum 512 SU; combined CPU+AI PBS cap 3 and maximum one running AI allocation. The separate CPU queue was empty immediately after PBS admission; do not infer it remains empty. Preserve queue positions and frozen payloads.

[H200 load-bracket plans and actual receipts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-full-load-followups-20261026/REVIEW.md). [H100 full N24 admission, controls and limits](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h100-equal-tp-bench-admission-20261026/REVIEW.md). No score exists yet for these three jobs.

## Latest reviewed performance

| Observation | Good output tokens/s | Joint latency pass | Interpretation |
|---|---:|---:|---|
|Historical H200 25366/25373/25487 mean|3044.400475|Retained passing observations|Historical cluster; not reproduced today|
|H200 exact legacy replay 26313|2830.923547|98.427850%|Actual operational parity; 7.012117% below old mean|
|H200 full modern graph/cap 64, 26317|2829.604300|98.426966%|Valid local full observation; no useful new gain|
|H200 full modern graph/native, 26319|2827.996286|98.424311%|Control for current N62/N66 bracket|
|H100 fresh full N54, 225227|2399.186728|98.015873%|0.347131% below retained 222551; no unchanged repeat|

All latest full observations have zero profiling request errors/cancellations, smoke 7/8 without regression and retrieval 12/12. Every score is raw AIPerf Goodput requests/s multiplied by 200. Do not mix H100/H200 scores as matched configurations. H100 retained best individual 222048 remains 2433.019859 tokens/s. Official full-set 99%-reference accuracy remains UNKNOWN; small checks do not certify it. Packaged AI primary remains unchanged N62 pending reviewed authorised promotion.

The complete four-arm H200 graph/admission study passes all local gates: disabled/cap 64 = 2807.325653, breakable/cap 64 = 2829.604300, breakable/native = 2827.996286, disabled/native = 2802.498990 tokens/s. Graph gains +0.793590% / +0.909806% and native admission changes -0.171931% / -0.056828% are below the prospective >1% useful-gain gate. Close this tuning branch without selecting a favorable subthreshold peak for confirmation. One ordered deployment per cell cannot prove causality. [Full review, actual runtime comparison and sealed evidence](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-factorial-review-20261026/REVIEW.md).

## Distinct current hypotheses

N62/N66 now bracket full native N64, changing only closed-loop client concurrency and corresponding workers. Earlier losing N66–N70 sweeps used short graph-disabled/cap 64 controls; this is an explicitly different runtime/protocol. Keep those losses. Review both actual results before widening; >1% useful valid gain versus contemporary N64 is needed before proposing independent confirmation. Full fixed-workload/source/runtime/semantic/raw-denominator/error/output gates remain.

H100 225228 F/0 in 6:39 passed eight distinct H100 device/source/metadata receipts, one independent eight-token semantic response and actual equal-TP send_kvcache/send_aux start/return markers on all four sender ranks without exceptions. Old 224560 lacked KV observer evidence because the checker watched a heterogeneous method; original failure remains. The new functional prerequisite is not a throughput or official accuracy pass. [Independent H100 review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h100-review-225227-225228-20261026/REVIEW.md).

225306 tests full N24 performance of one eight-GPU EAGLE unit. It preserves parent native serving/observer arithmetic and source pins; actual semantic/metadata gates precede scoring, then raw profile and local output gates. One unit is not a same-resource comparison against 16-GPU N54. A necessary per-unit feasibility threshold of 1235.581165 good tokens/s for a hypothetical 3% aggregate gain is not proof of linear scaling. Any future 16-GPU replica score must be actually measured. Do not scale or retry unchanged before reviewing the actual run.

26337 also passes small synthetic NIXL/UCX writes on 16 distinct H200s: 32 writes, 6,160,384 bytes total across three phases, all receiver buffers/sentinels validated. It repairs the earlier source-mount prerequisite failure. No model/SGLang bootstrap/real KV/TP collective/throughput is proven; do not relaunch the old failed full topology unchanged. [Component boundary](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-26337-20261026/REVIEW.md).

## Access, credit and admission

VPN and existing AI/CPU authenticated SSH channels worked at the latest admission. No phone-side DUO approval or exact session lifetime is claimed. Preserve healthy private session state; never capture it or restart it gratuitously. Selected AI project 59010042 snapshot label 26/10/2026-22:40:01: grant 64000, used 48199.780, balance 15800.220, In Doubt negative zero SU. Retain all 4000 SU old unreconciled maxima, including terminal 225227/225228, plus 512 SU for 225306; conservative planning headroom 11288.220 SU. Do not release reservations from runtime alone. Owner's earlier 30 October planning deadline remains.

PBS admission checks both own queues and selected project credit under CPU-before-AI locks. A parser initially rejected signed negative zero before any reservation/qsub; it was fixed/tested, remote checksums reverified and exactly one definite new receipt obtained. No uncertain attempt remains. No budget increase or other worker spending occurred. Read nscc-budget.json and actual receipts before another admission.

## Inspection, history and backup

Inspect tails/errors/concurrency, role-local queues/KV, transport/runtime, CPU/GPU/VRAM and cost. H100 225227 scored-admission envelope has 24 samples per role, decode activity 99.990%, prefill 91.542% / 91.427%, 72 HTTP 200 polls. Earlier allocation-wide means include startup and measure a different interval. Activity is not FLOPS; VRAM is not token occupancy; node-wide low CPU does not exclude a hot serving thread. Historical helper host-memory TiB labels were wrong: division from KiB by 1024 squared produces GiB; raw bytes and scores unchanged. [Correct window and units](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h100-score-window-225227-20261026/REVIEW.md). Uncalibrated host skew and sparse request-start envelopes are not exact phase clocks. Missing telemetry is not zero.

[Readable illustrated learning checkpoint](../reports/ai-research-learning-journey-20261023/FULL_WORKLOAD_CHECKPOINT_20261026.md), [complete journal](../reports/research-journey-20261019/journal/README.md), [preceding handoff with older losses/corrections](history/20261026-ai-before-1450-condense.md). Earlier snapshots in history are not live.

Edit active sources once. Capture explicit safe small milestones, screen/verify, commit with actual dates and push the existing private origin. Frozen raw evidence and large-object hashes are preserved; GitHub push does not upload the sibling external artifact store. No slide/submission/HPC payload changed in this continuation. Continue justified research when queue/budget/evidence permit; this never enables background Codex or schedules.

## New owner steering and actual admissions — 2026-10-26T17:31:58.694229+00:00

Owner removed all AI internal SU buffers. Twelve terminal local holdbacks totaling4512SU are released; historical maxima/terminal receipts remain audit metadata, without claiming individual charge reconciliation. Fresh selected AI balance15686.158SU, internal buffer0. [Policy proof](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h100-no-buffer-policy-20261026/POLICY-APPLIED.json).

H20026436 N62 and26438 N66 completed0:0 with2823.776622 and2826.104466 good tokens/s; both full local gates pass but no gain againstN64. Earlier active snapshots are historical. Actual next Slurm jobs26473 chunk6144 and26475 chunk4096 are submitted, 16H200/two nodes/17minutes each, fullN64;26475 afterany26473.

H100225306 F/127 after6:41: source/device/metadata/semantic gates pass, but external timeout cannot directly execute the PBS srun shell function. No benchmark ran. Root added that faulty boundary; derived R2 runs sourced shim inside timed Bash. Actual shim isolated-PATH regression reproduces127 and corrected0. R2 prepared, not yet submitted. Existing CPU read-only SSH command times out; one separate auth attempt did not establish a working channel. AI SSH works. Do not claim CPU queue is empty or restart VPN. No HPC payload/ledger changed.
