# TP4 prefill kernel screen: submitted, no result yet

Updated 2026-10-20T08:01:59.878719+00:00. The preceding H100 TP8 decode screen **222242 passes 256/256 cases** but finds no useful alternative: retain DeepGEMM and avoid a losing full-model pair. [Full comparisons and limits](../fp8-privatehome-20261020/RESULTS.md).

New H100 **222245.pbs111** is queued. It tests a distinct phase and geometry, **TP4 prefill QKV/O projections at M512/2048/4096/8192**, plus diagnostic M54. Native Triton versus DeepGEMM, same synthetic tensors, numerical guards and graph timing. Eight ranks/twenty cases each, separate eight-case provider preflight, rank 0 post-timing profiles at M8192. Eight GPUs/ten minutes, maximum 170.666667 SU. No model/SLA/accuracy claim. [Hypothesis, source evidence and acceptance rule](PLAN.md), [payload/static validation](validation.json), [receipt](pbs-receipts.json), [live PBS](live-pbs.txt).

H200 **24990/24928/24962/24964/24965** remain Priority-pending; all four model positions retained, total five. No cancellation/replacement in this step. [Fresh queue](live-slurm.txt). No additional H200 job until capacity frees.

Latest publication Used **37236.052 SU**, Balance **26593.281 SU**, In Doubt **170.667 SU**, queried 2026-10-20T08:00:09.090876+00:00. Old failed 222232 estimated 21.617778 and passed 222242 estimated 73.955556 SU are not posted: retain both full max reservations plus the new maximum, total **512 SU**. Conservative internal headroom **13251.948 SU** under unchanged 51000 cap/13000 buffer. [Unique-subset reconciliation](failed-accounting.json). Published balance already excludes In Doubt; do not subtract twice. Previous unchanged Used after first failed charge is a dated publication, not actual zero spending.

Next: collect only after terminal state, verify hashes and all 160 full cases separately from preflight, inspect paired GPU distributions and actual kernel traces, then apply the predeclared >=5% representative rule. The retained review-micro.py rejects missing cases, numerical/input/source/config/UUID failures and nonzero scheduler exit. Even a passing kernel screen only permits planning a real model pair; it cannot establish end-to-end improvement. No blind repeat or numeric relaxation if the candidate loses.

All work is in English, Qwen only; no submission package change, authentication restart or background Codex. Git captures are explicit; large artifact-store bytes still require separate off-host backup.

## Completed and reviewed — 2026-10-20T09:11:47.564445+00:00

222245 finished exit 0 in 4 minutes 8 seconds. **160/160 full cases** pass numerical/reference/cross-backend/input/source/config checks on eight distinct GPUs; eight unranked preflight cases are excluded. Nine finite positive timing samples per case and four nonempty native GPU traces verified. [Structured review](222245.pbs111-review.json), [sealed raw capture](collect-222245.json).

| Shape | Tokens M | DeepGEMM (us) | Triton (us) | Paired latency reduction (%) | Faster ranks /8 |
|---|---:|---:|---:|---:|---:|
| tp4-o-proj | 54 | 7.186 | 10.506 | -45.58 | 0 |
| tp4-o-proj | 512 | 10.435 | 14.759 | -40.96 | 0 |
| tp4-o-proj | 2048 | 35.074 | 56.747 | -62.58 | 0 |
| tp4-o-proj | 4096 | 68.111 | 114.484 | -67.50 | 0 |
| tp4-o-proj | 8192 | 140.443 | 229.988 | -62.46 | 0 |
| tp4-qkv | 54 | 9.560 | 16.415 | -72.03 | 0 |
| tp4-qkv | 512 | 17.206 | 25.272 | -45.73 | 0 |
| tp4-qkv | 2048 | 49.909 | 76.494 | -52.12 | 0 |
| tp4-qkv | 4096 | 80.346 | 136.985 | -70.63 | 0 |
| tp4-qkv | 8192 | 163.069 | 257.744 | -57.55 | 0 |

Negative reduction means longer candidate latency. Values are medians across eight GPU ranks and paired rank ratios, not independent full-model runs.

**Decision: retain DeepGEMM for this TP4 prefill regime.** Triton loses all eight ranks at every shape/M; all six representative >=5% criteria fail. At M8192, QKV is 57.55% slower and O projection 62.46% slower by median paired ratios. No full-model Triton pair and no unchanged retry. This closes the tested native default kernels, not every possible tuned/custom Triton implementation. The synthetic TP4 and earlier TP8 screens do not establish official quality or H200 timings.

The final PBS GPU accounting has cumulative-looking low-utilisation/power-violation counters longer than the four-minute job; do not treat them as job-local efficiency or throttling fractions. Raw statistics remain preserved. Exact UUID snapshots and actual traces are useful evidence; continuous phase hardware telemetry was not deployed in this isolated micro.

Estimated charge **70.542222 SU** reconciles together with prior failed 21.617778 and passed 73.955556 SU: published delta 166.116 SU matches 166.115556 within 0.01 SU rounding. Latest Used **37402.168 SU**, Balance **26597.832 SU**, In Doubt zero. All local reservations released; internal headroom **13597.832 SU** under unchanged 51000 cap/13000 buffer. [Final reconciliation](final-accounting.json). Own PBS queue empty at this query; H200 all five still Priority-pending. No new serving result.
