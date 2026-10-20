# Native DeepGEMM SM-budget screen

Updated 2026-10-20T09:16:33.708071+00:00. **222277.pbs111** is submitted and state **R** at this query. One H100 node/eight GPUs/ten minutes, maximum 170.666667 SU. This is an isolated synthetic kernel experiment; no serving score or official accuracy result exists. [Receipt](pbs-receipts.json), [fresh scheduler state](live-pbs.txt), [guarded submission](submit-pbs.py).

## What led here

TP8 decode screen 222242 passes 256 full cases and TP4 prefill screen 222245 passes 160. Both reject native default Triton: no faster rank at any tested shape/M. At prefill 8192 tokens, QKV is 57.55% slower and O projection 62.46% slower by median paired latency ratios. Keep DeepGEMM; no full-model Triton pair or unchanged retry. [Complete prefill result, every paired rank, numerical gates and cost](../fp8-prefill-tp4-20261020/RESULTS.md).

The new question holds native DeepGEMM fixed and changes its internal scheduling budget through its supported set/get_num_sms API: 132 control versus 120/96. SM is a streaming multiprocessor inside a GPU. All eight GPUs, tensor work, precision and inputs remain. This changes neither physical clock/power nor model topology. A private one-GPU/six-case provider preflight precedes 240 full cases. Nine samples per full case, rotated order, all prior numerical/input guards, native setter/getter checks and default restoration. Actual SM-bearing kernel traces must prove that each requested budget executed. [Predeclared plan, primary pinned source and thresholds](PLAN.md), [local validation](validation.json).

Only broad precompilation over unrelated Ms is disabled; exact test shapes still warm/JIT before timing and every native GEMM executes. This saves setup work, not tensor computation. The real source-hook AST fixture verifies the broad precompile gate; it does not prove GPU numerics. A micro winner still needs safe serving integration and a real controlled model pair: the global API may affect other callers, and CPU integration overhead is absent from the kernel measurement. No end-to-end speed prediction.

## Queues, budget and next review

H200 24990 and four model jobs 24928/24962/24964/24965 remain Priority-pending, total five; no new cancellation or sixth job. [Live Slurm query](live-slurm.txt). H100 only this new allocation is active; no overlap with completed 222245.

All preceding charges reconcile with published Used **37402.168 SU**, Balance **26597.832 SU**, In Doubt **-0.000 SU**, queried 2026-10-20T09:15:33.122635+00:00. Reserve only this new maximum 170.666667 SU; conservative internal headroom **13427.165333 SU** under unchanged 51000 cap/13000 buffer. [Pre-submit accounting](accounting-preflight.json). Earlier trial costs remain preserved; no duplicate prepayment deduction.

Review terminal hashes, all 240 full cases and six separate preflight cases, numerical/input/default-restoration/source/UUID guards, paired timings and six actual native traces. Apply >=5% median improvement with >=6/8 ranks positive at both shapes/M48/54/60/64 and no >5% median loss at M32, separately for each candidate. Otherwise keep 132. No blind retries, serving changes, official accuracy claim, package edit, authentication restart or background Codex.

## Completed native scheduler screen — 2026-10-20T09:20:20.459454+00:00

**222277 completes 240/240 full cases**, six separate unranked provider-preflight cases, all eight ranks/default restorations/input/numerical/source/UUID gates, and six native SM90 traces confirming 132/120/96 template budgets. Exit 0, allocated walltime 2:11, estimated **37.262222 SU**, ledger reconciled=False. This verifies actual activation, not only a logged setter. [Every rank and native kernels](222277.pbs111-review.json), [sealed capture](collect-222277.json), [accounting](post-screen-accounting.json).

| Shape | M | SM budget | Control 132 (us) | Candidate (us) | Paired latency reduction (%) | Faster ranks /8 |
|---|---:|---:|---:|---:|---:|---:|
| tp8-o-proj | 32 | sms_120 | 5.154 | 5.476 | -6.29 | 0 |
| tp8-o-proj | 32 | sms_96 | 5.154 | 5.446 | -5.99 | 0 |
| tp8-o-proj | 48 | sms_120 | 5.469 | 5.700 | -4.87 | 1 |
| tp8-o-proj | 48 | sms_96 | 5.469 | 5.500 | -1.41 | 3 |
| tp8-o-proj | 54 | sms_120 | 5.556 | 5.540 | -0.10 | 4 |
| tp8-o-proj | 54 | sms_96 | 5.556 | 5.391 | +2.65 | 8 |
| tp8-o-proj | 60 | sms_120 | 5.376 | 5.531 | -3.08 | 0 |
| tp8-o-proj | 60 | sms_96 | 5.376 | 5.481 | -1.94 | 2 |
| tp8-o-proj | 64 | sms_120 | 4.935 | 5.094 | -3.28 | 0 |
| tp8-o-proj | 64 | sms_96 | 4.935 | 5.055 | -2.22 | 0 |
| tp8-qkv | 32 | sms_120 | 7.857 | 7.898 | -0.21 | 1 |
| tp8-qkv | 32 | sms_96 | 7.857 | 7.845 | -0.06 | 4 |
| tp8-qkv | 48 | sms_120 | 8.268 | 8.181 | +0.82 | 6 |
| tp8-qkv | 48 | sms_96 | 8.268 | 8.203 | +2.53 | 6 |
| tp8-qkv | 54 | sms_120 | 8.309 | 8.366 | -0.16 | 3 |
| tp8-qkv | 54 | sms_96 | 8.309 | 8.089 | +2.73 | 8 |
| tp8-qkv | 60 | sms_120 | 8.185 | 8.224 | -0.47 | 2 |
| tp8-qkv | 60 | sms_96 | 8.185 | 8.117 | +0.71 | 5 |
| tp8-qkv | 64 | sms_120 | 7.823 | 7.845 | -0.01 | 4 |
| tp8-qkv | 64 | sms_96 | 7.823 | 7.782 | +0.33 | 7 |

Both candidates fail the predeclared consistent 5% gate: **retain 132; close 120/96** without unchanged repeats or serving changes. SM 96 helps both M54 matrices on 8/8 GPUs by 2.73%/2.65%, but other M values are mixed and O-proj M32 regresses 5.99%; SM 120 is generally flat/slower. These are kernel latencies, not serving gains.

The actual M54 QKV native tile is BLOCK_M64/BLOCK_N16 across all three budgets, with N1280: ceil(54/64)*ceil(1280/16)=80 logical output tiles. This motivates a **single separately declared 80-SM test with fresh 132 control**, rather than repeating 96/120 or scanning many numbers. It is an inference from tile geometry plus the modest M54 signal, not measured SM occupancy or predicted gain. Counterhypothesis: the native heuristic changes tiles or makes O projection slower, so both-shape representative gates remain unchanged. No global model setting will change without useful fully gated evidence and safe integration review.
