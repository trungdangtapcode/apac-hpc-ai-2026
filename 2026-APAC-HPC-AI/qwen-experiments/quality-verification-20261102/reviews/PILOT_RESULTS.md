# Pilot review: real accuracy, below the local 99% point gate

Reviewed **2026-11-03T00:59:14.841409+07:00, Vietnam time (UTC+7)**. All three allocations are terminal; both actual measurement runs complete with zero request errors. Failed 28367 is a separate pre-inference stock FP8 layout failure, retained without a score.

| Role | Job/configuration | Correct/total | Accuracy | Client duration | Output tokens | Length-limited outputs |
|---|---|---:|---:|---:|---:|---:|
| Local unchanged FP8 reference | 28371, two stock TP8/EP8 replicas, 16 H200 | 104/128 |81.25%|84.153432s|84729|12|
| Submitted candidate configuration | 28368, two TP4 prefills + TP8/EP8 decode, 16 H200 | 102/128 |79.6875%|82.668722s|87011|14|

Candidate/reference accuracy ratio = 102/104 = **0.9807692307692307 (98.076923%)**, below 0.99. The predeclared local pilot point gate therefore **FAILS**. This is not a measured full-set score or an organiser verdict. Do not claim PASS based on unchanged weights, change the parser after seeing answers, or hide this losing sample.

The 128-question sample is balanced across 14 categories; it is not the full 12032-question dataset distribution. There are 14 differing parsed answers: 5 reference-only correct, 3 candidate-only correct and 6 where both are wrong but choose different answers. Correctness is 99 both-correct and 21 both-wrong. A difference of two correct answers matters at this small denominator. Full-set measurement is the next test, not a reinterpretation of this pilot as passing.

## Inspection and limits

Independent raw-JSON replay reproduces the stored content, parser output and counts. Both use exact paired compiled prompts, tokenizer/template, deterministic adaptive shots, temperature 0/top_p 1, max 2048 and stop `Question:` at concurrency 16. All 128 IDs occur once per run, zero service errors and zero deadline skips. Source/token/prompt/precision identities are retained. Reference used native Triton MoE defaults; the candidate uses its submitted phase/backend configuration. This is whole-stack fidelity, not an isolated patch or kernel ablation.

Reference has 12 length endings and one unparsed output; candidate has 14 length endings and zero unparsed outputs. Parser fallbacks are retained, not omitted: 10 versus 13 final-standalone-letter extractions. The source-standard 2048 output limit is identical. Two reference-only correct items end at that limit on the candidate; this is an observation, not proof that a specific kernel or output budget caused the accuracy difference. No random guesses are substituted. Invalid/error records stay wrong in the denominator.

Candidate request latency mean/p95/max=9.032/27.422/27.510s; reference=8.949/27.244/29.191s. These are non-streamed CoT request latencies, not TTFT/ITL SLA measurements. Pilot generation throughputs ~1052.5 and 1006.8 output tokens/s are sizing evidence for this N16 workload, not the ranked N64 AIPerf score.

Reference GPU identity and pre-start memory/activity snapshots were collected; they do not establish steady-state utilisation. Candidate hardware NVML sampling was not collected, although accepted worker checks/logs identify Hopper and the H200 allocation. Role batch/queue/token-usage logs and transport/runtime logs are retained. No causal quality-loss diagnosis follows from these aggregates.

## Cost and next decision

Actual top-level occupancy: 28367 failed 103s=0.457778 GPU-hours; candidate 28368 completed 457s=2.031111; corrected reference 28371 completed 388s=1.724444. Total **4.213333 GPU-hours**, zero PBS SU. Pilot reservations are retired after cleanup; no child-step double counting.

Proceed with a **separately labelled full 12032-question comparison at client N64**, the candidate's declared production load, holding compiled prompts and generation/scoring fixed across roles. Do not pool pilot N16 answers with full N64 answers. Freeze disjoint full-set shard membership before inference and retain all answers/errors. A planned 8 shards/role (1504 questions each) needs 16 independent 17-minute allocations, maximum 72.533334 GPU-hours, zero PBS SU; the initial full shard will validate the forecast for the longer CoT workload. Prior N64 performance throughput is only a sizing forecast, not an observed full-quality rate. Admit within cap 5/shared locks and preserve every incomplete/failing shard; never drop questions or select best retry answers. Official BTC certification remains separate.
