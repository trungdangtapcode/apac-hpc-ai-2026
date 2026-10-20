# Private-home kernel retry — 2026-10-20T07:52:41.504271+00:00

No new serving score. H200's highest individual remains 3022.034919 good output tokens/s (24915, N62); independent exact repeat 24962 is pending. H100 remains 2433.019859 (222048, N54). Platforms are separate; official full-set reference accuracy remains unverified.

## What failed and what changed

Original H100 222210 failed FlashInfer import below read-only home; estimated 20.480 SU. Cache-routed 222232 passed imports and pinned-source checks but completed zero cases: six TVM FFI JIT directory errors and two TensorRT native directory aborts. Estimated 21.617778 SU. These are setup failures, not performance losses. Both terminal raw snapshots and frozen payloads are retained in the linked [failure review](../fp8-linear-micro-review-20261020/RESULTS.md). The first CPU fixture tested FlashInfer workspace routing only and was too narrow to certify the whole provider stack.

Derived v3 binds an empty private writable home at the existing HOME path inside the container, matching the already successful full-model worker contract. HOME's value is unchanged and real account authentication files are not copied or mounted. Explicit cache routing remains. A separate single-GPU provider preflight runs ten cases at M16/54, both projection shapes, all applicable backends, before launching eight independent full timing ranks. Preflight results are unranked and must not be merged with full timings. Full bench.py/config.json remain byte-identical to v2: same numerical/input gates, shapes, rotated backend order, 16 operations per graph, ten replays, nine samples. [Plan](PLAN.md), [actual wrapper CPU test](validate-privatehome.py), [validation](validation.json).

## Submitted and bounded

- H100 **222242.pbs111**, one node/eight GPUs/ten minutes, submitted 07:51 UTC; queued for memory availability at the latest retained query. No numerical or timing result yet. [Receipt](pbs-receipts.json), [pre-submit accounting](pbs-pre-submit.txt), [latest query](pbs-live-0753.txt).
- H200 **24990**, one node/eight GPUs/ten minutes; Priority-pending. Only old micro **24988** was cancelled while pending, at zero runtime. Four model jobs **24928/24962/24964/24965** retain their positions and payloads, total five active H200. [Receipt](slurm-receipts.json), [pending-only cancellation](old-slurm-cancellation.json), [queue](slurm-post-submit.txt).
- No model loading or model-score claim for either micro. No submission package, authentication or background Codex change.

## Credit and next decision

Published Used **37236.052 SU**, Balance **26593.281 SU**, In Doubt **170.667 SU**, queried 2026-10-20T07:51:25.210221+00:00. Published delta uniquely matches the first failed charge, 20.480 SU; that reservation is reconciled. The second failed charge is not yet posted, so retain its full maximum 170.666667 SU, plus new retry max 170.666667 SU. Conservative outstanding bound **341.333333 SU**, campaign headroom **13422.614667 SU** under unchanged 51000 cap and 13000 buffer. In Doubt is already withheld from the published balance; do not subtract it again. [Subset reconciliation proof](failed-accounting.json).

First require the real ten-case provider preflight to pass. Then inspect all eight full ranks (32 cases each), input integrity, numerical comparisons, graph samples and native kernel traces. Only a consistent representative improvement of at least 5% supports a bounded full-model control/candidate pair. Microseconds are not serving goodput and no direct end-to-end gain may be claimed. Preserve partial/failure evidence and do not loosen numerical gates. Fresh scheduler/ledger checks remain mandatory before later spending.
