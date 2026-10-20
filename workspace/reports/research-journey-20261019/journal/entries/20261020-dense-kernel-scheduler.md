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

## Native scheduler result — 2026-10-20T09:20:20.459454+00:00

222277 fully passes 240 cases and six actual native traces. Neither 120 nor 96 SMs meets the declared 5% representative threshold: keep 132. SM 96 has a modest M54-only +2.73% QKV/+2.65% O-proj on 8/8 ranks but mixed other batches and M32 O-proj loss 5.99%. Not a serving improvement. [All settings, rank distributions, numerical gates and next geometric hypothesis](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/deepgemm-sm-screen-20261020/RESULTS.md). Estimated charge 37.262222 SU, ledger reconciled=False; retained maximum 170.666667 SU, internal headroom 13427.165333 under unchanged caps. Own PBS queue empty; five H200 jobs remain pending. Earlier running snapshots below are historical.

The actual QKV tile geometry yields80 logical tiles at M54. A distinct80-SM pilot can test that exact boundary; it is not an unchanged96/120 repeat, a model promotion or a broad decreasing-SM sweep. Preserve both negative and small positive cases; do not relax the5% gate.

# 80-SM boundary pilot submitted

Updated 2026-10-20T09:23:02.323548+00:00. H100 **222279.pbs111** is **R** at the retained query; one node, eight GPUs, ten minutes, maximum **170.666667 SU**. No result is available for SM80. [Receipt](pbs-receipts.json), [live PBS](live-pbs.txt), [plan and fixed acceptance rule](PLAN.md).

The preceding **222277** passes all **240 full cases**, six separate provider-preflight cases, numerical/input/source/default-restoration/UUID guards and six actual native SM90 templates. Settings 120/96 fail the declared consistent 5% rule, so **132 remains the serving default**. At M54 alone, 96 reduces QKV/O-proj helper latency by 2.73%/2.65% on 8/8 ranks; other M values are mixed and O-proj M32 regresses 5.99%. These are synthetic kernel timings, not model throughput. [Every setting/rank, units and limits](../deepgemm-sm-screen-20261020/RESULTS.md).

The new candidate 80 targets the logical 80-tile QKV boundary observed in those traces; it is one geometry-supported point with a fresh 132 control, not a wide scan or unchanged 96/120 retry. Exact benchmark/cache code and numerical/graph controls are byte-identical to validated 222277. Four unranked provider-preflight cases precede 160 full cases; four actual traces must prove 132/80 kernel activation. [Tile evidence](tile-evidence.json), [payload validation](validation.json). Both shapes and M32/48/54/60/64 remain; no gate relaxed. This point closes the tested scheduler-budget family if it fails. A micro gain would still need safe caller/integration review and an independent full-model experiment.

Published Used **37439.430 SU**, Balance **26560.570 SU**, In Doubt **0.000 SU**, queried 2026-10-20T09:21:46.816377+00:00. Prior 222277 charge reconciles 37.262 SU and all older maxima are released. Reserve only the new maximum **170.666667 SU**; internal headroom **13389.903333 SU**, unchanged 51000 cap/13000 buffer. [Fresh accounting proof](accounting-preflight.json). No prepaid double subtraction or uncertain retry.

H200 **24990/24928/24962/24964/24965** all remain Priority-pending, cap five. No cancellation or sixth job. H100 only 222279 is active. Model bests remain H200 3022.034919 and H100 2433.019859 good output tokens/s, with official full-set reference accuracy unverified. No model/SLA/quality claim, package change, authentication restart or background Codex. [Live H200](live-slurm.txt).

## Scheduler family closed — 2026-10-20T09:26:13.430145+00:00

222279 passes 160 full cases and actual 132/80 traces, but 80 fails the declared useful-consistency gate: M54 QKV+5.17% versus O-proj+2.40%, other batches mixed. Keep 132 and close tested 80/96/120 budgets without a model tweak. Estimated cost 35.271111 SU pending ledger, retain maximum. [Complete cases, paired ratios, native proof and next model interaction](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/deepgemm-sm80-20261020/RESULTS.md). H100 own queue empty; H200 five jobs still Priority-pending. Next prepare the missing H100 HPC-Ops-prefill/chunk 8192 interaction against fresh 4096 at N54, not a repeat of the old auto-prefill 8192 loss. Serving peaks unchanged. Earlier running/queued snapshots below are historical.

