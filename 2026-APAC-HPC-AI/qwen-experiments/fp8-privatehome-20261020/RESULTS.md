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

## Completed H100 screen — 2026-10-20T07:58:29.424255+00:00

222242.pbs111 finished exit 0 in 00:04:20, estimated **73.955556 SU**, pending ledger publication. The private-home repair passes actual execution: ten unranked provider-preflight cases and **256/256 full cases**, all eight ranks with input/numerical/source/config guards, nine finite positive timing samples per case, eight distinct device UUIDs and four nonempty kernel traces. DeepGEMM's broad JIT warmup completed within the bounded preflight; the generic 10–20-minute warning was not an observed timeout and no warmup flag was changed. The preflight is excluded from all reported comparisons. [Complete structured checks and every paired rank](222242.pbs111-review.json), [sealed raw capture](collect-222242.json).

Positive reduction means the candidate takes less time; a negative value means longer latency. Medians are across eight GPUs, not independent full-model runs.

| Shape | M | Candidate | DeepGEMM median (us) | Candidate median (us) | Paired latency reduction (%) | Faster ranks /8 |
|---|---:|---|---:|---:|---:|---:|
| tp8-o-proj | 16 | flashinfer_deepgemm | 4.891 | 5.373 | -8.89 | 0 |
| tp8-o-proj | 16 | triton | 4.891 | 6.958 | -42.31 | 0 |
| tp8-o-proj | 31 | flashinfer_deepgemm | 5.102 | 5.683 | -11.32 | 0 |
| tp8-o-proj | 31 | triton | 5.102 | 6.946 | -36.02 | 0 |
| tp8-o-proj | 32 | triton | 5.127 | 6.904 | -34.91 | 0 |
| tp8-o-proj | 48 | triton | 5.408 | 6.962 | -28.71 | 0 |
| tp8-o-proj | 54 | triton | 5.554 | 6.997 | -25.78 | 0 |
| tp8-o-proj | 60 | triton | 5.355 | 6.988 | -30.49 | 0 |
| tp8-o-proj | 64 | triton | 5.024 | 6.998 | -39.79 | 0 |
| tp8-qkv | 16 | flashinfer_deepgemm | 8.484 | 8.318 | +2.34 | 6 |
| tp8-qkv | 16 | triton | 8.484 | 16.073 | -89.40 | 0 |
| tp8-qkv | 31 | flashinfer_deepgemm | 8.281 | 8.853 | -7.18 | 0 |
| tp8-qkv | 31 | triton | 8.281 | 16.608 | -100.76 | 0 |
| tp8-qkv | 32 | triton | 8.215 | 16.431 | -99.51 | 0 |
| tp8-qkv | 48 | triton | 8.128 | 16.541 | -103.26 | 0 |
| tp8-qkv | 54 | triton | 8.261 | 16.537 | -100.25 | 0 |
| tp8-qkv | 60 | triton | 8.083 | 16.534 | -104.18 | 0 |
| tp8-qkv | 64 | triton | 7.713 | 16.476 | -113.16 | 0 |

Decision: **retain DeepGEMM for TP8 decode attention projections on H100**. Triton loses every rank at every tested M; its M54 QKV call is about twice as slow and O projection about 26% slower. FlashInfer has only +2.34% median at QKV M16 (six positive ranks), while other small-M cases lose; this fails the consistent >=5% gate. At M>=32 its native path falls back to DeepGEMM, so a full-model FlashInfer toggle remains unjustified. Do not submit a full-model Triton/FlashInfer pair from this screen. Actual traces identify SM90 DeepGEMM versus Triton _w8a8_block_fp8_matmul plus native quantisation; summed trace durations are not critical-path shares.

This is a synthetic TP8 decode screen. It does not settle TP4 prefill projections at hundreds/thousands of tokens, MoE experts, official accuracy, or H200 portability. H200 micro 24990 is still Priority-pending alongside four model jobs; preserve their positions. A separate bounded TP4 prefill screen can test that distinct matrix regime before any full-model flag change.
