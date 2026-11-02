# Paired local accuracy verification

**Full-set accuracy jobs admitted — 2026-11-03T01:20:59.095638+07:00, Vietnam time (UTC+7):** Slurm accepted **28373 reference / 28375 candidate**, paired shard 0 of 8, **1504 questions each at concurrency 64**. Reference has produced all 1504 responses (1200 correct, 79.787234%, zero service errors); terminal cleanup is being checked, candidate has not produced a score. This first shard is 1/8 of the fixed 12032-question evaluation, not a full-set result. Remaining 14 planned allocations are held behind the first-pair runtime/coverage gate, not a winning-score gate. Total full stage at most 72.533334 H200 GPU-hours, zero PBS SU, own queue cap 5. Pilots remain 102/104=98.076923% below99%; no official BTC certification. Published ZIP and HPC unchanged.

**Reviewed pilot outcome — 2026-11-03T00:59:14.841409+07:00, Vietnam time (UTC+7):** reference 28371=104/128 (81.25%); candidate 28368=102/128 (79.6875%), ratio 98.076923% <99%: **local pilot point gate FAIL**, no request errors. Original 28367 failed FP8 layout before inference. [Full raw-response/runtime/cost analysis](reviews/PILOT_RESULTS.md). Pilot actual 4.213333 GPU-hours, zero PBS SU; all pilot reservations retired. Full 12032-question N64 stage being prepared, not yet submitted in this snapshot; no full-set or BTC certification claim. Published submission/HPC unchanged. Earlier queued/pilot-preparation states below are historical.

Updated **2026-11-03T00:30:37.968878+07:00, Vietnam time (UTC+7)**. The owner explicitly authorised research and actual quality measurement. Slurm accepted **28367 reference** and **28368 candidate**; both are **PENDING / Resources** in this actual observation. Admission receipts, frozen manifest and maximum reservation are under `admission/` and `frozen-pilot/`.

The reference uses two stock native FP8 TP8 replicas, one per node; this is an internal accuracy reference, not a colocated ranked Basic submission. The candidate preserves the accepted 28197 model-worker configuration and P/D transport path. Both use identical compiled questions, tokenizer/template, adaptive shots, greedy settings, 2048 output allowance and parser. Pilot concurrency 16 and 128 selected questions are distinct from the performance N64 point.

All **12032 questions** passed actual CPU tokenizer preflight, with zero unfit and no truncated/dropped questions. The original evaluator's prompt<2048 budget is honoured; shots distribution is 11714 at 5, 198 at 4, 91 at 3, 26 at 2 and 3 at 1. Seven local protocol fixtures and shell/Python checks pass. These are preparation facts, not measured quality. No model answers or accuracy ratio are available yet.

The two pilot allocations each request 16 H200/two nodes/max 17 minutes, combined maximum 9.066667 GPU-hours; zero PBS SU. Initial pilot serves runtime/API/scoring feasibility; it cannot certify full-set quality or BTC acceptance. After both pilots are reviewed, declare a bounded measured-duration full-set sharding envelope before admitting further jobs. The existing ranked ZIP and all HPC materials remain unchanged; broad performance research/autopilot stay stopped.

Actual scheduler snapshot:

```text
28368|ap42-qual-cand|PENDING|0:00|17:00|2|(Resources)
28367|qref-pilot|PENDING|0:00|17:00|2|(Resources)
```
