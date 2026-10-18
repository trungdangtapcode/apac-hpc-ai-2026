# H100 prefill gain repeats — 18 October 2026, 13:51 UTC

Job **221339.pbs111** independently repeats the N50 configuration with HPC-Ops in both prefill and decode: **2,371.341 good output tokens/s**, versus the original 221315 at **2,371.961**. Their descriptive mean is **2,371.651**. The repeat is **2.7009%** above the preceding matched decode-only control 221314 at 2,308.979; the original comparison was +2.7277%. These two observations closely agree, but do not constitute a statistical confidence interval. Fresh reversed-order control 221340 is still running.

Repeat joint latency success is **98.7838%**, mean TTFT **492.980 ms**, mean ITL **18.199 ms**. It passes terminal evidence seal, frozen payload, full 60/120/30 protocol, intended runtime/layout/precision, short-output nonregression and all 12 long retrieval checks. Runtime comparison explicitly allows only the main and inherited speculative prefill MoE runner to change from auto to HPC-Ops; speculative decoding remains disabled. Decode HPC-Ops, MNNVL, FlashInfer attention, weights, BF16 cache and prefetch stay matched. Official full-set accuracy at 99% of the organiser reference evaluation score remains unverified.

## New useful experiment

Submitted **221346.pbs111**, a full N50 benchmark of this repeated configuration followed by a separate concurrency 48 diagnostic: four prefill / 32 decode steps and 16 expected nonzero rank traces. The score precedes profiling; preserve all protocol and output checks. This changes only the post-score diagnostic switch and metadata, not worker execution or scoring. Frozen payload and syntax checks are in next-validation.json.

Why profile now? The previous 221284 profile contains auto-runner prefill and cannot establish the remaining cost after replacing that implementation. The new profile will support the next kernel or communication hypothesis rather than assuming that an old kernel-duration share remains applicable. Inspect actual HPC-Ops kernel names; old name-only MoE classification can miss them. Shares describe summed kernel durations, not wall time or predicted speedups. Require valid trace/rank coverage and diagnostic request success. Profile deferral/failure is separate from the scored result; never sacrifice quality checks to capture traces.

Verified PBS chain: **221340 → 221341 → 221346**. 221340 is the fresh decode-only N50 control; 221341 tests both-phase HPC-Ops at N52. At most three active jobs, one 16-GPU allocation running at a time, each 45 minutes / 1,536 SU maximum. No automatic further load increase. Keep existing queue positions and close failed/losing branches instead of unchanged retries.

H200 has no new completed measurement: **24573, 24574, 24575, 24588, 24589** remain pending Priority. The five-job bound is occupied, so no additional H200 submission. Previous highest observation remains 2786.696 pending its repeat and fresh same-load control.

## Reconciled credit

Ledger as of 18 October 21:40:01 SGT: Used **25,846.898 SU**, Balance **36,617.102 SU**, In Doubt **1,536 SU**. Its 897.706 SU increment reconciles terminal 221316 (15:14, 519.964 SU) and 221339 (11:04, 377.742 SU), within rounding. Both old reservations are released. New profile reserves at most1,536 SU; total outstanding maximum for 221340/221341/221346 is 4,608 SU. Headroom under the unchanged internal 51,000 SU cap is **20,545.102 SU**. The 13,000 SU buffer is internal planning, not organiser quota. Reported Balance already excludes prepayment; do not deduct it twice.

No slide/package update or organiser upload. Codex autopilot remains off; no AI schedule or background watcher was launched. All raw artifacts, reviewers, accounting and returned-ID receipts are retained.
