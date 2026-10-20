# One bounded unobserved H100 receive-interval check

## Prior evidence and uncertainty

The fully reviewed observed pair gives interval1 222049 = 2395.311 and interval2 222050 = 2406.802 good output tokens/s, +0.480%. Observer-off interval1 222048 = 2433.020, while observer on/off differs −1.550% in one pair. Different nodes/order and sampling can contribute; this is not an isolated overhead estimate. Raw request-mean ITL breaches are zero/four/five, so the positive mean-throughput difference is insufficient to promote interval2. All local full gates pass; official accuracy remains unverified.

The native pinned disaggregated receiver source is already verified in both images. Interval2 can skip receive/pull/broadcast on alternate decode steps while preserving extend-like receipt, all model forwards and tokens. Hypothesis: its small positive observed result persists without enabling SGLang metrics/resource sampling. Counterhypothesis: the gain is noise, or delayed admission worsens tails. One direct unobserved check separates that question from instrumented deployment; no subtraction of the on/off delta predicts the score.

## Exact two-run sequence

1. h100-hpc-n54-recv2-unobserved-60: candidate, interval2, observer off.
2. h100-hpc-n54-recv1-unobserved-control-61: fresh control, interval1, observer off; PBS afterany dependency on the candidate.

Candidate-first reverses the previous control-first order, without claiming randomisation or removal of all node/cache confounds. Both derive from fully reviewed 222048 submitted bytes. Only the candidate's native decode receive interval changes in the inference command. No `--enable-metrics` or resource sampler runs in either scored phase. Resource files remain in the frozen bundle but are disabled by the same environment setting; absence of scored hardware telemetry is intentional and must be recorded as not collected.

Both retain N54, chunk4096, both-phase HPC-Ops, two TP4/EP1 prefill workers, TP8/EP8 decode, same native FP8 checkpoint/BF16 KV, FA3 prefill/FlashInfer decode, MNNVL AUTO+PDL, graphs1–64, NIXL, round robin and complete streaming 4000/200 and 60/120/30 protocol. All short and 12 long output checks and separate post-score N48 CPU/GPU diagnostics remain byte-identical. Heavy profiling is not part of the ranked score.

## Gates, cost and stop rule

Review frozen hashes, actual resolved arguments and all ranks; intended delta is only scheduler_recv_interval on decode (plus random seeds), metrics false on all roles and speculative decoding disabled. Require terminal evidence, raw per-request protocol/SLA/error counts and short/long output nonregression. Inspect tail latency/concurrency and available batch/queue/KV/CPU/GPU diagnostics, with missing uniform telemetry marked explicitly. Do not pool H100 and H200 or equate kernel sums with wall time.

A >=1% useful fully gated gain warrants a later independent controlled confirmation, not immediate adoption. Smaller/flat/losing results close this particular interval2 setting under the current credit priority; no automatic interval4, load increase or unchanged retry. Preserve failures. Official full-set 99%-reference quality remains open.

At preparation published Used 36308.194 SU, Balance 27691.806, In Doubt zero; all three previous charges reconcile and reservations are released. New maximum reserve **3072 SU**, two 16-GPU jobs with 45-minute ceilings; estimated actual charges are not guaranteed. Internal headroom after maximum reserve is **11619.806 SU** under unchanged 51000 cap and 13000 project buffer. Query real queue/credit before reserve/qsub, remain at most three active PBS and exactly one running 16-GPU allocation, use a serial afterany chain and retain reservations on any uncertain submission. No authentication restart, package change or background Codex.

Evidence: ../research-followup-20261020-h100-restored/RESULTS.md and the retained exact receiver/source checks in ../research-followup-20261020-recv2/PLAN.md. This plan continues the active authorised research after the explicit H100 reconnection request.
