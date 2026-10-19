# Research continuation and submitted batch — 19 October 2026

Recorded at 2026-10-19T12:02:20.997548+00:00. The user corrected the repeated idle H100 queue: continue researching and submitting justified experiments, rather than only reporting that losing branches stopped. The earlier decision to leave all H100 research stopped after N56 and Tree was an incorrect interpretation of branch-level stopping rules. Root AGENTS.md and the current handoff now record the corrected workflow. Background Codex remains disabled.

## Jobs actually submitted

| Platform | Job | Trial | Maximum allocation |
|---|---|---|---|
| H100 / PBS | 221827.pbs111 | Fresh N54 both-phase HPC-Ops control, followed by a separate profile | 16 GPUs / 45 min |
| H100 / PBS | 221828.pbs111 | Same N54, change prefill chunk 4096 → 6144 only | 16 GPUs / 45 min |
| H100 / PBS | 221829.pbs111 | Same N54, change prefill all-reduce protocol to Simple only; separate profile | 16 GPUs / 45 min |
| H200 / Slurm | 24819 | N58 repeat and separate profile of DeepGEMM prefill / chunk8192 / HPC-Ops decode | 16 GPUs / 17 min |

Verified PBS chain **221827 → 221828 → 221829**, using afterany dependencies; at most one PBS 16-GPU allocation runs. Queue states at submission were Q/H/H. H200 now has five pending jobs: older 24733/24736/24737/24738 retain their positions, with 24819 added. These are submission receipts, not performance results. No new score is claimed.

## Why these are new tests

The [plan and official references](PLAN.md) connects the tests to the sealed profile, prior outcomes and fresh controls. Tree remains closed. Simple changes communication protocol with automatic algorithm selection retained, and must prove actual GPU execution. Chunk6144 tests a new interaction with HPC-Ops prefill, whereas the earlier H100 chunk8192 loss used auto prefill. No further load increase or changed model precision is involved.

The H200 profile targets the actual best-observed deployment rather than inferring its bottleneck from H100. Its source ran in 9:54; the requested bound remains 17 minutes. Profiles occur after ranked scoring and do not change the 4000/200, 60/120/30 protocol. All non-target operational files and decode branches are verified identical to their source; new raw runtime, quality and profile proof are still required.

## Budget and next review

Fresh pre-submit ledger: Used **29391.644 SU**, Balance **34608.356 SU**, In Doubt **0**. The three PBS jobs reserve a maximum **4608 SU**; this is not a measured charge. Internal remaining headroom under the unchanged 51000-SU cap is **17000.356 SU**, keeping the 13000-SU project buffer. No uncertain submissions occurred; never retry an uncertain qsub blindly. Current credit publication may lag allocations; retain reservations until the actual ledger reconciles.

Review each completed job independently; do not wait for the whole chain before drawing conclusions or preparing the next justified experiment. If a slot is available, continue evidence-backed research within the cap rather than requesting the same continuation again. A failed candidate stops that candidate, not unrelated work. Freeze matched controls, retain losses and establish actual backend execution before promotion. Highest observations remain H200 2938.628 and H100 2430.891 good output tokens/s pending these results; official accuracy is unverified.

Raw evidence: [PBS receipts](pbs-receipts.json), [PBS verified dependencies](pbs-post-submit.txt), [Slurm receipt](slurm-receipts.json), [Slurm queue](slurm-post-submit.txt), [frozen pilots](pilots.json), [static validation](validation.json), [pre-submit ledger](pbs-pre-submit.txt). No VPN restart, authentication, AI schedule, official package promotion or slide change.

## Next experiment already prepared

[Next research and source evidence](NEXT_RESEARCH.md) records a frozen dense FlashInfer-prefill N54 comparison, a future support-first NVLS probe and the exact limits of the published accuracy specification. The attention trial is prepared locally but not uploaded, submitted or reserved while the three-job PBS cap is occupied. The submitted payloads above are unchanged. Read standby-pilot.json before selecting the next free slot; review the new control first.
