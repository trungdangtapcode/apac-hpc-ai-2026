# Numerical HPC result schema for the shared atlas

The owner clarified that Result must contain numerical measurements with explicit metric names and units, like the AI track. Assessments are separate. The HPC result record therefore identifies the metric, numeric value (or null when unavailable), unit, preferred direction, job and run scope, measured horizon and exact source. This is presentation of retained evidence, not a new scoring formula.

Solver mean seconds/step is lower-is-better and includes every prescribed measured interval after step 1. Timing change is 100×(candidate/control−1); negative means lower time, not the same percentage as throughput increase. Repeat drift is the ratio of later/earlier same-treatment means minus 1. Graph/interface counts are proxy metrics, never solver performance. Setup-only or incomplete experiments have no valid matched solver score. Null means unmeasured or unreviewed; it is never replaced by zero. Different jobs/platforms/horizons stay in their own contexts.

The UI shows metrics in the Result block, with units and run context, and keeps the scientific assessment/limits in a separate section. Hover and milestone inventory reuse the same records. The latest reviewed native result is job 2294735; new independent 40-step ABBA job 2294800 is accepted and running at the recorded snapshot, but has no completed score. The website must not assign the earlier result to the new job.

Validation includes schema checks, missing-data handling, exact source-linked numeric values, browser rendering/hover/mobile width and preservation of AI component data and notes. Build with the existing HPC-only atlas route. The existing GitHub Pages workflow publishes only reviewed generated HTML; deploy and live verification receipts are added when available.

## Implemented schema

All 15 milestones contain 51 metric records. Each record has `key`, `label`, `value` (number or null), `unit`, `direction`, `scope`, `job_id`, `horizon`, and `source`. Metrics are grouped by their own job; no cross-job means are invented. The Result panel renders numbers and units with job/horizon context, hover and milestone table use numeric summaries, and Assessment/Limitations are separate. Schema/source/type checks and Chromium desktop/mobile/hover/AI-track tests pass. Existing AI component files, embedded AI data and AI research-note bodies remain unchanged.
