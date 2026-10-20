# Cache-only retry submitted; original failure retained

Original H100 222210 failed on all eight ranks while importing FlashInfer, before any numerical/timed case. The missing explicit FlashInfer workspace caused writes to read-only /home/users. The [failed review](../fp8-linear-micro-review-20261020/RESULTS.md), payload, stderr, hashes and account are retained; no kernel result exists for that attempt.

Derived bundles add unique writable job/rank dependency caches before imports and assert the real FlashInfer workspace uses them, without changing HOME. The config, run script and numeric/timing body remain byte-identical. The exact dependency AST fixture reproduces the previous path and validates eight writable cache trees; actual GPU execution remains separately checked.

| Platform | New job | Retained state |
|---|---|---|
|H100|222232.pbs111|R at the final-live.json timestamp|
|H200|24988|Priority-pending|

Only pending standalone H200 micro 24983 was cancelled with a pending-state filter, before execution (00:00). Four model jobs 24928/24962/24964/24965 keep their positions and frozen payloads. There are five active H200 jobs including the replacement, within cap. Original receipts remain historical; cancellation and new receipts are separate files. No submitted bundle was edited in place.

The H100 retry has already written **eight writable cache preflight records** in the live progress read. No numerical/timing cases were visible in that read, which is live and unsealed. Do not count this as a completed kernel screen or a model gain. Actual later imports, source hash, kernel checks, graph capture, numerical bounds and complete rank results still require review.

## Accounting

The original failed job used 8 GPUs for 72 seconds, estimated 20.480 SU. At fresh retry submission, the published Used delta was zero and the final charge had not posted. Its full old 170.666667 SU maximum is therefore retained as TERMINAL_PENDING_LEDGER_CONSERVATIVE_RESERVE. The new retry reserves max 170.666667 SU. Total conservative outstanding bound is 341.333333 SU, internal headroom 13443.094667 SU under unchanged 51000 cap/13000 buffer. Pre-retry publication Used 37215.572, Balance 26613.761, In Doubt 170.667; those values are a dated publication, not a live unreserved balance. Once the final failed-job delta matches 20.480, reconcile and release its old maximum; never subtract prepayment twice.

One running PBS allocation only. No model weights loaded, serving result, official accuracy, numerical threshold relaxation, native hardware-guard bypass, clock/power change, package edit, VPN restart or background Codex. The original bounded kernel plan/gates remain in PLAN.md and ../fp8-linear-micro-20261020/PLAN.md.
