# H100 HPC-Ops prefill chunk interaction: actual submissions

Updated 2026-10-20T09:30:58.728352+00:00. No new model score is available. The dense-kernel search is closed at native defaults: **132-SM DeepGEMM remains**, with no Triton or per-shape SM patch deployed. All negative/mixed cases are retained. [240-case native budget screen](../deepgemm-sm-screen-20261020/RESULTS.md), [160-case boundary screen](../deepgemm-sm80-20261020/RESULTS.md), [160-case TP4 prefill comparison](../fp8-prefill-tp4-20261020/RESULTS.md).

| Job | Status at query | Prefill | Decode | N | Allocation |
|---|---|---|---|---:|---|
|222281.pbs111|R|HPC-Ops, chunk 4096|HPC-Ops, unchanged|54|16 H100, <=45 min|
|222282.pbs111|H|HPC-Ops, chunk 8192|Identical|54|16 H100, <=45 min|

The second depends on **afterany:222281**, verified by the scheduler. No overlapping allocation. Both use the same uniform resource sampler, phase markers, full 60/120/30 protocol and 4000/200 workload, FP8 checkpoint/BF16 KV, topology and output checks. Candidate worker inverse-diffs exactly to control after reverting only prefill chunk 8192→4096. No official accuracy claim. [Receipts](pbs-receipts.json), [latest PBS](live-pbs.txt), [predeclared hypothesis/thresholds/source evidence](PLAN.md), [frozen validation](validation.json).

The older H100 chunk 8192 trial used **auto prefill**, applying HPC-Ops only to decode. The new HPC-Ops-prefill8192 interaction is distinct. Compare the fresh equally observed pair, not H200 or old unobserved peaks. A useful >=1% pair gain needs all local gates and later independent confirmation; failure/loss closes this exact setting without an unchanged retry or blind chunk/load growth.

## What to collect and inspect next

Use the existing full-model PBS collector only after each terminal state, write collect-JOBNUMBER.json into this directory, then run review-pbs.py. It checks sealed payload/protocol/SLA/error/short/12-long gates and compares actual resolved ServerArgs with observed 222049, allowing only random seeds plus candidate prefill 4096→8192. It explicitly requires HPC-Ops preflights, unchanged decode attention/MNNVL ranks, BF16 KV and inference-mode policy. It writes a paired comparison only if both full local reviews pass. This prepared reviewer has syntax/static validation only; no future result is implied.

Inspect uniform hardware/server samples and all 16 separate diagnostic rank traces as well. Use existing observability tools with new run IDs, phase manifests, actual UUID/role/host mapping, field-support and coverage checks. Do not apply a historical hardcoded inspector without adapting its job list. Cross-node clock skew remains uncalibrated; deduplicate node counters. Profiles occur after scoring, do not add their traffic to the benchmark or treat summed kernel durations as critical-path fractions. The official >=99%-reference full-set accuracy remains unverified.

## Credit and other queue

Pre-submit publication queried 2026-10-20T09:29:00.721061+00:00: Used **37439.430 SU**, Balance **26560.570 SU**, In Doubt **0.000 SU**. Last completed micro 222279 estimated 35.271111 SU is unposted, so retain its whole 170.666667 maximum in addition to the pair's 3072 maximum. Conservative outstanding bound **3242.666667 SU**, internal headroom **10317.903333 SU**, unchanged 51000 campaign cap/13000 buffer. [Reconciliation proof](prior-accounting.json), [pre-submit ledger](pbs-pre-submit.txt). Prepayment is not deducted twice. Future credit claims require a fresh query.

H200 24990/24928/24962/24964/24965 are all Priority-pending, exactly five active jobs; no cancellation or sixth job. [Actual queue](live-slurm.txt). Serving bests are unchanged: H200 3022.034919 and H100 2433.019859 good output tokens/s, with platform/replication/official-quality limits in CURRENT. No package, authentication or background Codex change. Git source/evidence captures are explicit; external large artifacts still need separate off-host copy.
