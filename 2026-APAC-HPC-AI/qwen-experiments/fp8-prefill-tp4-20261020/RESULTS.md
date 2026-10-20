# TP4 prefill kernel screen: submitted, no result yet

Updated 2026-10-20T08:01:59.878719+00:00. The preceding H100 TP8 decode screen **222242 passes 256/256 cases** but finds no useful alternative: retain DeepGEMM and avoid a losing full-model pair. [Full comparisons and limits](../fp8-privatehome-20261020/RESULTS.md).

New H100 **222245.pbs111** is queued. It tests a distinct phase and geometry, **TP4 prefill QKV/O projections at M512/2048/4096/8192**, plus diagnostic M54. Native Triton versus DeepGEMM, same synthetic tensors, numerical guards and graph timing. Eight ranks/twenty cases each, separate eight-case provider preflight, rank 0 post-timing profiles at M8192. Eight GPUs/ten minutes, maximum 170.666667 SU. No model/SLA/accuracy claim. [Hypothesis, source evidence and acceptance rule](PLAN.md), [payload/static validation](validation.json), [receipt](pbs-receipts.json), [live PBS](live-pbs.txt).

H200 **24990/24928/24962/24964/24965** remain Priority-pending; all four model positions retained, total five. No cancellation/replacement in this step. [Fresh queue](live-slurm.txt). No additional H200 job until capacity frees.

Latest publication Used **37236.052 SU**, Balance **26593.281 SU**, In Doubt **170.667 SU**, queried 2026-10-20T08:00:09.090876+00:00. Old failed 222232 estimated 21.617778 and passed 222242 estimated 73.955556 SU are not posted: retain both full max reservations plus the new maximum, total **512 SU**. Conservative internal headroom **13251.948 SU** under unchanged 51000 cap/13000 buffer. [Unique-subset reconciliation](failed-accounting.json). Published balance already excludes In Doubt; do not subtract twice. Previous unchanged Used after first failed charge is a dated publication, not actual zero spending.

Next: collect only after terminal state, verify hashes and all 160 full cases separately from preflight, inspect paired GPU distributions and actual kernel traces, then apply the predeclared >=5% representative rule. The retained review-micro.py rejects missing cases, numerical/input/source/config/UUID failures and nonzero scheduler exit. Even a passing kernel screen only permits planning a real model pair; it cannot establish end-to-end improvement. No blind repeat or numeric relaxation if the candidate loses.

All work is in English, Qwen only; no submission package change, authentication restart or background Codex. Git captures are explicit; large artifact-store bytes still require separate off-host backup.
