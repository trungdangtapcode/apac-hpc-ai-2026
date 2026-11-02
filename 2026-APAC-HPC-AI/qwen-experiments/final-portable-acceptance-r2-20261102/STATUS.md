# Readiness repair acceptance: 28197

Observed 2026-11-02T08:00:53.498588+07:00, Vietnam time (UTC+7). Definite Slurm acceptance: **28197**. Fresh own-user queue:

```text
28197|PENDING|0:00|17:00|(Resources)
```

SUBMITTED, not a passing result. One corrected 16-H200/two-node/N64 job, maximum 17 minutes / 4.533334 GPU-hours, zero PBS SU. Original 28194 is FAILED/22:0 before scoring and fully cleaned up, with actual top-level 334 seconds / 1.484444 GPU-hours. Its old maximum was retired once. The additional bounded reservation is separate; no H100/HPC or automation change.

Sources were captured/pushed in 9d472cb7 before submission. [Exact readiness-only patch](gateway-readiness.patch), [local fixtures](validation.json), [independent review summary](REVIEW.md), [frozen derived payload](FROZEN_PAYLOAD.json), [receipt](admission/submission-receipt.json), [reservation](admission/reservation.json), [preserved original failure](../final-portable-acceptance-20261102/FAILURE_28194.md).

Only deploy-and-benchmark.sh and its checksum differ from the failed packaged entry. The added gate waits for actual qwen model registration before continuing. Serving parameters, reader fixes, both semantic-route gates and the entire official benchmark are unchanged. Outputs stay in this delivery copy; published ZIP/folder still retain the old entry pending successful qualification and deliberate publication of a fix.

After execution require whole top-level success, valid gateway model list and two semantic receipts, locked official raw benchmark, summary/performance-gate pass and cleanup. No score or official quality result exists at this pending observation. Preserve any failure; do not submit another unchanged retry or claim an optimisation gain.
